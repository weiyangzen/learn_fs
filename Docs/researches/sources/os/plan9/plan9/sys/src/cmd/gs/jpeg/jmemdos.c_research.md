# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdos.c

MS-DOS-specific system memory manager backend. It supports near allocations, far allocations, direct DOS temporary files, XMS extended-memory backing store, and EMS expanded-memory backing store.

The file requires `USE_MSDOS_MEMMGR` and enforces `MAX_ALLOC_CHUNK < 64K`. Small allocations use `malloc/free`; large allocations use `farmalloc/farfree`, `_fmalloc/_ffree`, or ordinary `malloc/free` depending on compiler and memory model.

Backing store selection tries XMS first, EMS second, and DOS files last. XMS access uses the XMS 2.0 move API and handles odd byte counts specially. EMS access uses LIM/EMS 4.0 move-region calls with packed/misaligned field macros. File backing store uses generated temp names from `TMP`, `TEMP`, or the current directory and calls assembly helpers from `jmemdosa.asm`.
