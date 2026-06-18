# File Research: sources/os/bsd/openbsd-src/sys/sys/swap.h

Swap device userland reporting and control constants.

This header defines `struct swapent`, the user-visible swap-entry record containing device id, flags, total/in-use block counts, priority, and path. It defines `swapctl` commands for enabling, disabling, counting, querying stats, changing priority, and setting dump device, plus swap flags for in-use, enabled, busy, and fake/in-construction state.

Kernel builds also define `NETDEV` as the synthetic device id for NFS swap.

Filesystem/storage relevance: direct storage relevance. Swap can be backed by block devices or network storage, and dump-device selection overlaps with low-level storage-device management.
