# File Research: sources/os/plan9/9front/sys/src/9/port/parse.c

Common control-message parser and command-table lookup helper.

Key responsibilities:
- Estimates field count for a raw byte buffer.
- Allocates one `Cmdbuf` containing pointer array plus a null-terminated copy of the command.
- Strips one trailing newline and tokenizes whitespace-delimited fields.
- Formats command errors with quoted original fields in `cmderror()`.
- Looks up `Cmdtab` entries with optional wildcard `*` and argument-count validation.

Important behavior:
- User-process command buffers larger than `READSTR` are rejected.
- UTF content is not interpreted for field splitting; whitespace bytes are ASCII-only.
- `cmderror()` does not return.

Role:
- Used throughout device control-file implementations.
