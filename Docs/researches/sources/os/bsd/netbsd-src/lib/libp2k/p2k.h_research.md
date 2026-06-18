# File Research: sources/os/bsd/netbsd-src/lib/libp2k/p2k.h

Public p2k API header. It declares the opaque `struct p2k_mount` and entry points for one-shot filesystem runs, one-shot disk filesystem runs, explicit initialization/cancel, setup for normal or partitioned filesystems, and the PUFFS main loop.

The API depends on `rump/ukfs.h` for partition descriptors and is installed as a rump-facing public header.
