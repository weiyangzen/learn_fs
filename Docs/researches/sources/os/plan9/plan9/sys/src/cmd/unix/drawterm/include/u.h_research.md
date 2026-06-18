# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/u.h

Top-level drawterm compatibility include.

Key contents:
- Selects `unix.h` or `9windows.h` through platform macros.
- Includes `lib.h`, `user.h`, and `dtos.h`.
- Undefines several syscall-like names to avoid exposing host/libc conflicts after setting up drawterm’s own namespace.

Role in this group:
- The first include in most drawterm source files, establishing host and Plan 9 compatibility definitions.

Notable risks:
- Include ordering is critical because this file deliberately manipulates many global macros.
