# File Research: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.h

## Purpose
Declares the malloc bdev creation/deletion interface and option structure.

## Main Contents
- `spdk_delete_malloc_complete`, the async delete callback type.
- `struct malloc_bdev_opts`, carrying name, UUID, block count/size, physical block size, optimal I/O boundary, metadata size/layout, DIF type, DIF location, PI format, and NUMA ID.
- `create_malloc_disk()` and `delete_malloc_disk()` prototypes.

## Dependencies
Includes SPDK standard and bdev module declarations.

## Risks and Notes
The `name` field is a mutable `char *` but is duplicated during creation. Callers must fully initialize defaults such as physical block size and NUMA ID before calling `create_malloc_disk()`.
