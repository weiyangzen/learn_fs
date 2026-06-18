# File Research: sources/os/bsd/netbsd-src/sys/sys/iostat.h

Defines disk/tape/NFS I/O statistics structures and kernel maintenance APIs. `io_sysctl` is the 64-bit-alignment-safe exported stats format. `io_stats` is the in-kernel TAILQ-linked state with transfer, byte, seek, busy, wait, and timestamp accounting.

Kernel functions initialize, allocate, rename, find, free, mark wait/busy/unbusy, and record seeks. Filesystem and block device drivers interact with this through device activity accounting. Risks include counter consistency, time accounting around busy/wait transitions, and preserving sysctl structure layout for userland tools.
