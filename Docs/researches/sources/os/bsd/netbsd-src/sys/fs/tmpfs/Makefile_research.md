# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/Makefile

Read completely: 7 lines.

This kernel include makefile installs `tmpfs_args.h` under `/usr/include/fs/tmpfs` through `bsd.kinc.mk`.

Important interactions: it exposes only the mount-argument ABI, not tmpfs internal kernel structures.

Security/reliability notes: no runtime behavior.
