# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/print.c

- Role: Provides Plan 9-style `print`, `fprint`, `sprint`, `snprint`, and `seprint` wrappers over `doprint`.
- Behavior: Formats into stack buffers or caller buffers, writes to file descriptors for `print`/`fprint`, and restores `printcol` after string-formatting calls.
- Integration: Used throughout u9fs for diagnostics and string assembly.
- Risks/notes: `sprint` uses a fixed 4096-byte bound even though the caller’s buffer size is unknown; use `snprint`/`seprint` where bounds matter.
