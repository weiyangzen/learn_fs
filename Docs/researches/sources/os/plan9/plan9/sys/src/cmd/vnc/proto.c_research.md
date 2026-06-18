# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/proto.c

Low-level RFB/VNC protocol I/O helpers.

Key responsibilities:
- Initializes and terminates `Vnc` Bio input/output state.
- Reads and writes big-endian chars, shorts, longs, points, rectangles, CoRRE rectangles, pixel formats, byte blocks, and strings.
- Provides a special unbuffered `vncrdstringx()` for negotiation steps that must bypass Bio.
- Flushes output and handles hung-up connections through `vnchungup()`.
- Serializes writes with `vnclock()`/`vncunlock()`.
- Provides debug hex dump and `vncgobble()` discard helper.

Important behavior:
- RFB numeric byte order is encoded manually.
- Read/write failures call `vnchungup()` rather than returning errors.
- `vncrdstring()` allocates NUL-terminated memory for protocol strings.

Risks:
- Allocation uses `assert`, so malformed huge string lengths can terminate the process or exhaust memory.
- Most helpers are fatal-on-error rather than recoverable.
