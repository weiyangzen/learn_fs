# File Research: sources/os/bsd/netbsd-src/lib/librump/Makefile

Read completely: 17 lines.

Builds the core `librump` kernel component library from the sys/rump rumpkern makefile. It disables full RELRO, points `RUMPTOP` at `../../sys/rump`, depends on `librumpuser`, uses warning level 3 because kernel code is not ready for stricter sign-compare warnings, and suppresses cast-function-type warnings for selected kernel-derived sources.
