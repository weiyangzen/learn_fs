# File Research: sources/os/bsd/dragonflybsd/sys/sys/idr.h

`idr.h` defines a kernel-only integer ID to pointer mapping API compatible with Linux conventions, including support for NULL pointers.

It declares `struct idr_node`, `struct idr`, and APIs to find, replace, remove, remove all, destroy, iterate, allocate new IDs, allocate above a starting ID, pre-grow, initialize, and allocate within a range. The structure tracks node array size, last/free indices, expansion count, maximum wanted ID, and a token for synchronization.

`idr_preload()` and `idr_preload_end()` are Linux-compatibility no-ops in this implementation.
