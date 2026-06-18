# File Research: sources/os/plan9/9front/sys/src/9/port/syscallfmt.c

System call argument and return formatter for Plan 9 syscall tracing.

Key responsibilities:
- Builds human-readable syscall entry strings in `syscallfmt()`.
- Builds syscall return strings, error strings, and timing data in `sysretfmt()`.
- Formats user strings safely after `validaddr()` checks and bounded NUL search.
- Formats read/write buffers as pointer plus printable ASCII preview, replacing non-printables with dots.
- Handles per-syscall argument layouts for file, process, segment, mount, read/write, stat, and compatibility syscalls.
- Stores trace text in `up->syscalltrace` under `up->debug`.

Dependencies:
- Uses syscall number/name tables from `/sys/src/libc/9syscall/sys.h`.
- Uses process debug locks, `validaddr`, `evenaddr`, `fmtstrinit`, `fmtstrflush`, and Plan 9 syscall argument conventions.

Notable behavior:
- Read/write data previews are capped at 64 bytes.
- `EXEC` traces argv by walking user pointers until nil.
- Return formatting knows which syscalls return pointers and which should use `up->syserrstr` on failure.
- A source comment notes “WE ARE OVERRUNNING SOMEHOW,” but the code itself bounds copied string/data previews.
