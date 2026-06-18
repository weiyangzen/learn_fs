# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dmmain.c

## Purpose

`dmmain.c` is a Macintosh Classic/Carbon example wrapper for running Ghostscript through the shared-library API using Metrowerks CodeWarrior SIOUX. It connects Ghostscript stdio, polling, and display callbacks to a Mac event loop and QuickDraw window.

## Main Components

- Global display format requests 32-bit RGB-style output with unused first byte, 8-bit components, big-endian layout, and top-first rows.
- `IMAGE` tracks one Ghostscript display device instance: handle, device pointer, Mac window, scrollbars, PixMap handle, update timing, and linked-list membership.
- `gsdll_stdin`, `gsdll_stdout`, and `gsdll_stderr` bridge Ghostscript stdio to SIOUX/std C streams.
- `gsdll_poll` processes Mac events cooperatively and returns `e_Fatal` when the app is quitting.
- `display_callback display` implements Ghostscript display-device hooks.
- Window helpers create, invalidate, resize, scroll, and repaint QuickDraw-backed image windows.
- `main` initializes Mac/SIOUX state, injects `-sDEVICE=display` and `-dDisplayFormat=...`, creates a Ghostscript instance, runs startup PostScript, exits, and then waits for user dismissal.

## Display Flow

1. `display_open` allocates and links an `IMAGE`, then creates a window.
2. `display_presize` rejects incompatible display formats.
3. `display_size` maps Ghostscript's raster buffer into a Mac `PixMap` and updates scrollbars.
4. `display_sync` and `display_page` invalidate the window and poll events.
5. `display_update` rate-limits redraws based on elapsed time.
6. `doUpdateWindow` copies visible pixels from the source PixMap into the window port, respecting scrollbar offsets.

## Filesystem Relevance

There is no filesystem implementation. The file is relevant to the broader Plan 9 tree only as vendored Ghostscript platform glue. It may read from stdin or non-interactive streams, but it does not manage filesystems or storage.

## Risks / Portability Notes

- This code is tied to deprecated Classic Mac OS / Carbon APIs, QuickDraw, and SIOUX.
- The display format is strict; mismatches return `e_rangecheck`.
- User input handling uses a custom SIOUX event-loop workaround to avoid modal console behavior.
- Image lifetime is manual: PixMaps, windows, and heap allocations are disposed in display close paths.
