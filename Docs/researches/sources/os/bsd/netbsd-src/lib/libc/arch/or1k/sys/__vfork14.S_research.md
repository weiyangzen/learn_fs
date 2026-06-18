# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__vfork14.S

This file implements or1k `__vfork14`. It uses the standard syscall macro, then adjusts the secondary return register `r12` so the child returns zero and the parent returns the child PID in `r11`.

It is the vfork-specific parent/child return-value adapter. Failure handling is inherited from `SYSCALL(__vfork14)`.
