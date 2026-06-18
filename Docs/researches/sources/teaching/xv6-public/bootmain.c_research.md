# File Research: sources/teaching/xv6-public/bootmain.c

C half of the boot loader.

Key behavior:
- Reads the ELF kernel image from disk starting at sector 1 into scratch memory at `0x10000`.
- Validates `ELF_MAGIC`, iterates program headers, loads each segment to its physical address, and zero-fills BSS.
- Jumps directly to the ELF entry point.
- Uses programmed I/O against IDE ports `0x1f0`-`0x1f7`.
- `readseg` rounds reads down to sector boundaries and may read extra bytes.

Scope and limits:
- Ignores ELF segment flags.
- Has no filesystem support; it reads raw sectors from the boot disk.
