# File Research: sources/virtualization/spdk/module/bdev/null/bdev_null.h

This header is the internal public interface for the null bdev module. It declares the delete completion callback type, `struct null_bdev_opts`, and the create/delete/resize functions implemented in `bdev_null.c`.

`struct null_bdev_opts` captures all creation-time geometry and metadata fields: name, UUID, logical and physical block sizes, block count, metadata size, preferred write/unmap hints, DIF type, DIF metadata placement, and DIF PI format. The API separates `bdev_null_create()`, asynchronous `bdev_null_delete()`, and synchronous `bdev_null_resize()`.

The header is consumed by RPC code and by the module implementation. Callers are expected to provide a valid options struct, and ownership of string fields remains with the caller except that `bdev_null_create()` duplicates the name internally.
