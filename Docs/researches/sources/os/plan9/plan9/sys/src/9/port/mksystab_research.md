# File Research: sources/os/plan9/plan9/sys/src/9/port/mksystab

Purpose: rc/sed/sam generator for syscall declarations and syscall name tables.

Key logic:
- Reads `/sys/src/libc/9syscall/sys.h`.
- Emits include, `typedef long Syscall(ulong*)`, and syscall function declarations.
- Generates `systab[]` indexed by syscall numbers, mapping unused `SYS_X*` entries to `sysdeath`.
- Generates `sysctab[]` string names, with some display-name rewrites.
- Emits `nsyscall`.

Dependencies and integration:
- Uses Plan 9 `sed`, `tr`, and `sam`; depends on exact formatting of libc syscall header.
