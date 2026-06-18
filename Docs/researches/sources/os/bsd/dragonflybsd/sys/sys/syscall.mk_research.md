# File Research: sources/os/bsd/dragonflybsd/sys/sys/syscall.mk

Generated make fragment listing machine-independent syscall stub object files.

Key contents:
- Defines `MIASM`, a backslash-continued list of syscall `.o` targets.
- Object names mirror syscall names such as `read.o`, `open.o`, `__sysctl.o`, `set_tls_area.o`, `openat.o`, `getrandom.o`, and `futimesat.o`.
- Omits obsolete numeric syscall holes and contains only active/generated stubs.

Important behavior:
- Generated from `syscalls.master` by `make sysent`.
- Must remain aligned with syscall numbering and prototypes even though it does not encode numbers directly.
- Used by build rules for assembling/linking syscall entry stubs.

Research notes:
- This is build metadata for the syscall ABI surface.
- Divergence from `syscall.h`/`sysproto.h` would show up as missing or stale syscall stubs.
