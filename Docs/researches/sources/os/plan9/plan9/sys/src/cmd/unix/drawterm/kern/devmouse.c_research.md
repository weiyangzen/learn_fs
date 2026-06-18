# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmouse.c

Implements mouse and cursor device `#m`.

Key behavior:
- Exposes `.`, `cursor`, and `mouse`.
- Allows only one open of `mouse`.
- Reading `cursor` returns cursor offset, clear mask, and set mask.
- Writing `cursor` installs a supplied cursor, or resets to arrow if the payload is too short.
- Reading `mouse` blocks until queued mouse movement/button data or a screen reshape event is available.
- Mouse events are returned in Plan 9 textual format beginning with `m`; reshape events begin with `t`.
- Writing `mouse` can reposition the host pointer through `mouseset`.

Dependencies:
- Uses global `mouse`, `cursor`, `screen`, `gscreen`, and screen cursor hooks from drawterm screen code.

Notable risks:
- Single-reader mouse model matches Plan 9 semantics but limits concurrent consumers.
