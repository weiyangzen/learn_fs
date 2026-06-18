# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/util.c

General Abaco utilities for allocation, runes, fonts, colors, forms, URL validation, external pipelines, images, text normalization, refresh batching, and new-window placement.

Key responsibilities:
- Provides checked allocation/string/rune helpers and min/max.
- Converts bytes to runes and manages `Runestr` copies.
- Computes dimension specs for frames and tables.
- Manages font path defaults/user overrides and lazy font opening.
- Caches solid-color images by RGB value.
- Sends plumber messages and percent-encodes query strings.
- Validates absolute URLs with a regexp.
- Runs external filter pipelines with `/bin/rc`.
- Parses content-type parameters.
- Converts `Memimage` image data into display `Image` or placeholder images.
- Splits wrappable text items on whitespace for better layout.
- Queues and flushes page refresh/redraw/status updates.
- Chooses a target column/window for newly opened pages.

Important behavior:
- `flushrefresh()` is called while the row is locked and updates render, status, URL, and tag state.
- `addrefresh()` increfs the page window until flush drains the refresh entry.
- `fixtext()` applies to top-level items and all table cell content.
- `makenewwindow()` prefers active column, selected page column, source page column, then last row column.

Dependencies:
- Uses libhtml types, Plan 9 draw/memdraw/thread/plumb/regexp, Abaco page/window/layout APIs, and external rc commands.

Notable risks:
- The URL regexp only recognizes schemes with `://`, excluding valid `mailto:` style URLs despite listing `mailto`.
- `getimage()` placeholder/image conversion assumes display image loading succeeds and consumes `ci->mi`.
- Refresh batching depends on correct window refcounts to avoid use-after-free during async page loading.
