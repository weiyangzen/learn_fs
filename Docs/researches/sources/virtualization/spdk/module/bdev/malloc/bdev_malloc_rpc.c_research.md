# File Research: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc_rpc.c

## Purpose
Provides JSON-RPC methods to create and delete malloc bdevs.

## Main Entry Points
- `bdev_malloc_create` decodes geometry, metadata, DIF, UUID, optimal boundary, and NUMA options, calls `create_malloc_disk()`, and returns the created bdev name.
- `bdev_malloc_delete` decodes the bdev name and calls `delete_malloc_disk()`.

## Internal Mechanics
The RPC layer builds `struct malloc_bdev_opts` directly from the generated decode context. `numa_id` defaults to `SPDK_ENV_NUMA_ID_ANY`. The core create function duplicates the optional name, so the decoded string can be freed after the call.

## Dependencies
Uses `bdev_malloc.h`, SPDK JSON-RPC, string/log helpers, and generated RPC autogen contexts.

## Risks and Notes
`physical_block_size` is optional and defaults to zero in the decode context unless the generator provides another default; the core create path rejects non-512-aligned values but accepts zero alignment-wise, which can create a bdev with zero physical block size if not normalized elsewhere.
