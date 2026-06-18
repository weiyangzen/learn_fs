# File Research: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.h

## Purpose
Declares the lvol bdev module's internal control API and shared data structures for lvstore/lvol operations.

## Main Contents
- `struct lvol_store_bdev` links an `spdk_lvol_store` to its base bdev, current request, removal flag, and global list entry.
- `struct lvol_bdev` embeds the public bdev and links it to its lvol and lvstore pair.
- Prototypes cover lvstore create/destroy/unload/rename/lookup, lvol create/snapshot/clone/external clone/resize/read-only/rename/destroy, bdev-to-lvol lookup, external snapshot device creation, shallow copy, and setting an external parent.

## Dependencies
Includes SPDK lvol, bdev module, blob_bdev, and internal lvolstore headers.

## Risks and Notes
This header exposes many asynchronous operations with callback contracts but no explicit ownership annotations; callers must follow the implementation's callback/lifetime rules.
