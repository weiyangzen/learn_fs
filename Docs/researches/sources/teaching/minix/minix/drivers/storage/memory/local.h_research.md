# File Research: sources/teaching/minix/minix/drivers/storage/memory/local.h

## Purpose

Declares linker-provided symbols for the embedded image ramdisk and defines convenient macros for its address and size.

## API Surface

- `_binary_imgrd_mfs_start`, `_binary_imgrd_mfs_end`: symbols emitted by `objcopy`.
- `imgrd`: pointer to the embedded ramdisk bytes.
- `imgrd_size`: byte size computed from the linker symbol difference.

## Dependencies

Depends on the memory driver Makefile producing `imgrd.mfs.o` with predictable binary-object symbol names.

## Risks

The size computation casts symbol addresses to `size_t`; it assumes the binary object symbols are in the same address space and ordered as expected.
