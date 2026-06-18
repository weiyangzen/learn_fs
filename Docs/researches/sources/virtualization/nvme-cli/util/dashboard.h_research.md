# File Research: sources/virtualization/nvme-cli/util/dashboard.h

## Role

`dashboard.h` declares the public API for the live dashboard implementation in `dashboard.c`. It exposes an opaque `struct dashboard_ctx`, an event enum, render/control functions, and lifecycle functions.

## API Surface

- `enum event_type` defines normalized dashboard events. Negative/zero values cover error and timeout; positive values cover key press, Escape, arrow up/down, Return, quit, NVMe uevent, and SIGWINCH.
- Getter/setter functions expose header rows, footer rows, data rows, data start index, refresh interval, and visible frame data rows.
- Reverse-video helpers set or reset highlighted row indices separately for data, header, and footer sections.
- `dashboard_draw_frame()` renders the current memstream contents or redraws after scroll changes.
- `dashboard_wait_for_event()` blocks until an input, timeout, resize, uevent, quit, or error event occurs.
- `dashboard_init()` creates a dashboard context and returns the writable memstream.
- `dashboard_reset()` resets dashboard state and clears the terminal.
- `dashboard_exit()` restores terminal/process state and frees resources.

## Dependencies

Only includes `<stdio.h>` directly, because callers need `FILE *`. The implementation relies on many POSIX/Linux facilities but keeps those hidden behind the opaque context.

## Research Notes

The header makes the caller responsible for supplying correct row counts before rendering. The API does not expose direct ownership of `dashboard_ctx`; callers must use `dashboard_exit()` after successful `dashboard_init()`.
