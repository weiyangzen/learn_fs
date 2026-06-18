# File Research: sources/virtualization/libnbd/lib/debug.c

Implements handle-level debug flag and debug callback dispatch.

Key functions:
- `nbd_unlocked_set_debug` / `get_debug`: toggle or read `h->debug`.
- `nbd_unlocked_clear_debug_callback`: frees the installed callback.
- `nbd_unlocked_set_debug_callback`: transfers callback ownership into the handle.
- `nbd_internal_debug`: formats a message, preserves `errno`, uses current error context if none is supplied, then calls the callback or writes to stderr.

Interactions:
- `internal.h` wraps this with `debug` and `debug_direct` macros guarded by `if_debug`.
- Error context comes from `errors.c`.

Research notes:
- Debug logging is designed to be safe on error paths by preserving `errno`.
