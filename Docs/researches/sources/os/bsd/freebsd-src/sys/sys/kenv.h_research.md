# File Research: sources/os/bsd/freebsd-src/sys/sys/kenv.h

Defines constants for the `kenv(2)` syscall: get, set, unset, dump, dump loader environment, and dump static environment. Name and value syscall limits are both 128 bytes.

Kernel builds expose global environment state: dynamic environment flag, lock, kernel and machine-dependent environment pointers, static environment/hints buffers, and active `kenvp`.
