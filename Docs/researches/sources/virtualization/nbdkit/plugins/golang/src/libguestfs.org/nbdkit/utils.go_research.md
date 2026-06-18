# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/utils.go

This file exposes small Go utility wrappers around nbdkit C helper functions.

Key behavior:
- cgo imports `nbdkit-plugin.h` and defines `_nbdkit_debug` and `_nbdkit_error` wrappers because cgo cannot call varargs functions directly.
- `Debug` sends a string to `nbdkit_debug`.
- `Error` sends a string to `nbdkit_error`.
- `SetError` calls `nbdkit_set_error`.

Integration:
- Used by `nbdkit.go` error mapping and by example plugins for debug logging.
- Relies on `pkg-config: nbdkit`.

Risk:
- `C.CString` allocations in `Debug` and `Error` are not freed, which can leak for repeated calls.
