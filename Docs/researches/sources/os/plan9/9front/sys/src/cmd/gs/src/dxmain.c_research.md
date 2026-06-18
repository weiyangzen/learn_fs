# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmain.c

## Scope

GTK-based Ghostscript shared-library frontend that installs stdio callbacks, optionally creates a GUI display callback, injects `-dDisplayFormat=...`, initializes the Ghostscript API, runs `systemdict /start get exec`, exits, and maps Ghostscript return codes to process exit status.

## Key Behavior

- `gsdll_stdin`, `gsdll_stdout`, and `gsdll_stderr` bridge Ghostscript I/O to Unix stdio while pumping GTK events.
- Maintains an `IMAGE` list keyed by Ghostscript display `handle` and `device`.
- Implements the `display_callback` table for open, close, resize, sync, page, update, and separation metadata.
- Creates GTK windows with scrollable drawing areas and optional CMYK/separation controls.
- Converts display-device buffers into GDK-compatible RGB/gray/indexed output for native 8-bit, native 16-bit, gray, RGB, CMYK, and separation formats.

## Dependencies

Uses GTK/GDK, Unix `read`, Ghostscript client API `iapi.h`, error constants from `ierrors.h`, and display-device format definitions from `gdevdsp.h`.

## Risks And Invariants

- Display buffers are owned by Ghostscript; `display_size` stores `pimage` and must not free it.
- `rgbbuf` and `cmap` are per-image conversion resources and must be freed on resize/preclose.
- Separation handling assumes at most `IMAGE_DEVICEN_MAX` components.
- There is a likely off-by-one guard issue: `display_separation` rejects `comp_num > IMAGE_DEVICEN_MAX`, but valid indices are `< IMAGE_DEVICEN_MAX`.
