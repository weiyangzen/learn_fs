# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/sys.c

This small file provides syscall stubs used by the amd64 C compiler support environment. It defines `_sysargs`, declares `_callsys`, and wraps selected Plan 9 syscalls: `getpid`, `pread`, `pwrite`, `close`, `open`, `create`, `_exits`, `dup`, `errstr`, `brk_`, and `sbrk`.

Each wrapper fills `_sysargs` with a syscall number and arguments, then calls `_callsys`. `sbrk` uses a private negative selector rather than a normal syscall number, matching the surrounding toolchain support conventions.

Filesystem relevance is direct for hosted compiler/tool execution: `open`, `create`, `pread`, `pwrite`, and `close` are the filesystem I/O primitives the compiler runtime uses to read sources and emit objects.
