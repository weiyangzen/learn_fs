# File Research: sources/virtualization/nbdkit/server/debug.c

Purpose: Implements verbose debug output and exported hexdump/hexdiff debug helpers.

Logging behavior:
- Debug output is disabled unless `verbose` is true.
- `debug_common` preserves the incoming `errno` across formatting and output.
- Messages are first formatted into an inner string, then C-string-escaped into an outer string with a standard prologue.
- The prologue includes `program_name`, optional `process_name`, thread-local name, optional instance number, and `debug:`.
- Non-server public debug calls use terminal coloring when stderr is a tty.

Public/internal entry points:
- `nbdkit_vdebug` and `nbdkit_debug` are exported for plugins/filters.
- `debug_in_server` is the server-internal implementation behind the `debug()` macro.
- `internal.h` deliberately prevents direct server use of `nbdkit_debug`.

Hex helpers:
- `nbdkit_debug_hexdump` formats 16-byte rows with offset, two hex groups, and printable ASCII.
- `nbdkit_debug_hexdiff` emits old/new rows only where bytes differ, marking rows with `-`, `+`, or space.
- Both handle unaligned starting offsets and preserve row offsets.

Dependencies:
- Uses `open_memstream`, ASCII classification, alignment and rounding helpers, and thread-local naming APIs.
