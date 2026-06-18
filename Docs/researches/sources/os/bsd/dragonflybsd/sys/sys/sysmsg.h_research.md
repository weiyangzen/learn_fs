# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysmsg.h

Kernel syscall message/result carrier.

Key contents:
- Kernel-only `struct sysmsg`.
- `sm_result` union supports pointer, int, long, `size_t`, two file descriptors, 32-bit, 64-bit, `off_t`, and `register_t` results.
- Stores `sm_frame`, the trapframe for saved user context.
- Stores `extargs`, a `union sysunion` used when more than six syscall arguments are needed.
- Provides aliases such as `sysmsg_result`, `sysmsg_fds`, `sysmsg_offset`, and `sysmsg_frame`.

Important behavior:
- The struct is packed.
- File descriptor return storage is `long fds[2]` so it maps to two 64-bit registers on 64-bit architectures.
- `struct sysmsg` usually precedes syscall arguments in `union sysunion`.

Research notes:
- This is the kernel-side ABI carrier tying syscall handlers to machine trap state and generated argument unions.
