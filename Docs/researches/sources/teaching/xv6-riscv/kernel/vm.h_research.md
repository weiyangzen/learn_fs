# File Research: sources/teaching/xv6-riscv/kernel/vm.h

Defines `sbrk` allocation mode constants:
- `SBRK_EAGER`
- `SBRK_LAZY`

Filesystem relevance: lazy allocation affects whether user buffers passed to file syscalls are physically mapped before `copyin()`/`copyout()` touches them.
