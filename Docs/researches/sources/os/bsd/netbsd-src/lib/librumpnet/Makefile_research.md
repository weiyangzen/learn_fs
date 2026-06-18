# File Research: sources/os/bsd/netbsd-src/lib/librumpnet/Makefile

Read completely: 12 lines.

## Purpose
Builds the `librumpnet` library from the rump networking makefile fragment.

## Main Responsibilities
- Disables full RELRO with `NOFULLRELRO=yes`.
- Sets `RUMPTOP` to the kernel rump tree.
- Declares a dependency on `librump`.
- Sets `WARNS=3` because the kernel code is not ready for `-Wsign-compare`.
- Includes `${RUMPTOP}/librump/rumpnet/Makefile.rumpnet`.

## Filesystem Relevance
Indirect. This is networking rump-library build glue, but `librumphijack` can route sockets to rump networking and filesystem tests often depend on rump networking transports.

## Dependencies
- `../librump`.
- Kernel rump networking makefile fragment under `sys/rump`.
