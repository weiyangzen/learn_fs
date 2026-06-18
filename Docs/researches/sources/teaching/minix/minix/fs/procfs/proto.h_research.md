# File Research: sources/teaching/minix/minix/fs/procfs/proto.h

`proto.h` declares ProcFS's internal module interfaces. It covers buffer initialization/append/result functions, `/proc/cpuinfo` generation, service-directory initialization and hooks, tree initialization and VTreeFS hook functions, PID-slot conversion, out-of-inodes reporting, and load-average utility retrieval.

The prototypes expose the service's main extension points around VTreeFS: lookup-time tree refresh, getdents-time expansion, read-time generator dispatch, and future readlink handling.
