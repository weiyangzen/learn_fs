# File Research: sources/teaching/minix/minix/fs/procfs/Makefile

This makefile builds the ProcFS service as program `procfs`. It compiles buffer management, CPU info, main/tree hooks, PID generators, root-file generators, service-directory support, and utilities.

It adds include paths for MINIX, MINIX filesystem headers, and MINIX servers. ProcFS links against `libvtreefs` and `libfsdriver`, reflecting that its file tree and inode lifecycle are delegated to VTreeFS rather than a custom disk-backed inode/block layer. The service build is finalized through `<minix.service.mk>`.
