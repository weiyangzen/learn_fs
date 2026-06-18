# File Research: sources/os/plan9/9front/sys/src/9/port/mksystab

System-call table generator from `/sys/src/libc/9syscall/sys.h`.

Key responsibilities:
- Emits syscall include and `typedef uintptr Syscall(va_list);`.
- Generates external syscall function declarations from `#define` names.
- Declares `sysdeath`.
- Generates indexed `systab[]` entries, mapping reserved `sys_x*` slots to `sysdeath`.
- Generates indexed `sysctab[]` syscall-name strings with selected display-name rewrites.
- Emits `nsyscall`.

Dependencies:
- Uses `sed`, `tr`, and Plan 9 `sam` scripting.
- Assumes syscall constants are in `/sys/src/libc/9syscall/sys.h`.

Notable risks:
- The generator is tightly coupled to formatting and naming in `sys.h`.
