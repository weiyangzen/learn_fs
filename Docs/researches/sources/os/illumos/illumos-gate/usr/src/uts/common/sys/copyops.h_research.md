# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/copyops.h

`copyops.h` defines the kernel copy-operation interposition vector. `copyops_t` contains hooks for byte copyin/copyout/string copy operations, typed fetch/store of 8/16/32/64-bit user words, and `physio`.

The comments explain this is used for fault handling, watchpoints, and pxfs-style interposition, generally only after page faults to avoid overhead. Kernel exports install/remove/check copyops on a thread and expose `default_physio`.
