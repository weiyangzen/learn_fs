# File Research: sources/os/bsd/netbsd-src/sys/sys/kcpuset.h

Declares opaque kernel CPU-set operations. It supports allocation, cloning, destruction, copyin/copyout from user `cpuset_t`, bit operations, set comparisons, intersection/merge/remove, first-set queries, atomic variants, and export to 32-bit word arrays.

It is used by affinity-sensitive subsystems including scheduling, interrupt distribution, and IPIs. Key risks are correct lifetime management with `kcpuset_use/unuse`, atomic vs non-atomic operation selection, and validation of user buffer sizes during copyin/copyout.
