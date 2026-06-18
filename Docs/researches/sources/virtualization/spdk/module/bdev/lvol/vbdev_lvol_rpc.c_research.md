# File Research: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol_rpc.c

## Purpose
Implements the JSON-RPC surface for logical volume stores and logical volumes, including snapshots, clones, external parents, shallow-copy progress, resize, inflate/decouple, listing, and deletion.

## Main Entry Points
- Lvstore RPCs: `bdev_lvol_create_lvstore`, `bdev_lvol_rename_lvstore`, `bdev_lvol_delete_lvstore`, `bdev_lvol_get_lvstores`, and `bdev_lvol_grow_lvstore`.
- Lvol RPCs: `bdev_lvol_create`, `bdev_lvol_snapshot`, `bdev_lvol_clone`, `bdev_lvol_clone_bdev`, `bdev_lvol_rename`, `bdev_lvol_resize`, `bdev_lvol_set_read_only`, `bdev_lvol_delete`, and `bdev_lvol_get_lvols`.
- Parent/copy RPCs: `bdev_lvol_inflate`, `bdev_lvol_decouple_parent`, `bdev_lvol_start_shallow_copy`, `bdev_lvol_check_shallow_copy`, `bdev_lvol_set_parent`, and `bdev_lvol_set_parent_bdev`.

## Internal Mechanics
`vbdev_get_lvol_store_by_uuid_xor_name()` enforces that callers identify a lvstore by exactly one of UUID or name. Most lvol operations resolve a bdev by name, verify it belongs to the lvol module via `vbdev_lvol_get_from_bdev()`, and then invoke the core asynchronous helper.

Size arguments are exposed in MiB and converted to bytes before calling lvol APIs. Listing lvstores reports UUID, name, base bdev, total/free clusters, I/O unit size, cluster size, and max growable size. Listing lvols reports alias, UUID, name, thin/snapshot/clone/esnap/degraded flags, allocated clusters, and parent lvstore identity; only lvols with nonzero refcount are listed.

Shallow copy tracking uses a process-local incrementing operation ID and a linked list of status entries. Start returns the operation ID immediately. Check reports copied/total cluster counts and state; completed or errored entries are removed when checked.

Deletion has extra degraded-lvol lookup logic: it first tries normal bdev name/alias lookup, then UUID lookup, then splitting `lvs_name/lvol_name` in-place.

## Dependencies
Uses SPDK JSON-RPC, bdev lookup APIs, string/log helpers, generated RPC autogen contexts, and `vbdev_lvol.h`.

## Risks and Notes
Several decode failures are reported as JSON-RPC internal errors. Shallow-copy status is retained until checked after completion or error, so clients must poll to free status entries. `bdev_lvol_delete` mutates the decoded `name` string when parsing `lvs/lvol` degraded lookup.
