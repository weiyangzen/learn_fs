# File Research: sources/os/bsd/netbsd-src/lib/librumpdev/Makefile

Read completely: 12 lines.

Builds the rump device component library from `${RUMPTOP}/librump/rumpdev/Makefile.rumpdev`. It disables full RELRO, depends on `librump`, uses warning level 3 for kernel-derived code, and otherwise delegates source selection to the sys/rump makefile fragment.
