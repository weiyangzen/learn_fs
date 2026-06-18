# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemdos.c

Purpose: MS-DOS-specific system memory-manager backend.

Major features:
- Near allocations.
- Far allocations.
- Direct DOS temporary-file backing store.
- XMS extended-memory backing store.
- EMS expanded-memory backing store.

Important behavior:
- Requires `USE_MSDOS_MEMMGR`.
- Enforces `MAX_ALLOC_CHUNK < 64K`.
- Small allocations use `malloc/free`.
- Large allocations use `farmalloc/farfree`, `_fmalloc/_ffree`, or ordinary `malloc/free` depending on compiler and memory model.
- Default max memory is `DEFAULT_MAX_MEM`, or 300 KB if not overridden.

Backing store:
- Selection order is XMS first, EMS second, DOS files last.
- XMS access uses the XMS 2.0 move API and handles odd byte counts specially.
- EMS access uses LIM/EMS 4.0 move-region calls with packed/misaligned field macros.
- File backing store generates names from `TMP`, `TEMP`, or current directory and uses assembly helpers from `jmemdosa.asm`.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jmemsys.h`, and the assembly routines declared from `jmemdosa.asm`.

Notes:
- Historical DOS backend; not a Plan 9 native memory path.
