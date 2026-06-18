# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/dev.c

## Purpose

`dev.c` builds and tears down pNFS blocklayout device-id nodes. It decodes the server's block volume XDR description, resolves the volume graph into usable Linux block devices, maps logical layout offsets to device offsets, and manages SCSI persistent-reservation registration for SCSI-backed volumes.

## Main Responsibilities

- Decode `pnfs_block_volume` records for simple, slice, concat, stripe, and SCSI volume types.
- Resolve simple device signatures through the blocklayout userspace pipefs helper via `bl_resolve_deviceid()`.
- Resolve SCSI volumes through `/dev/disk/by-id/` paths using dm-mpath, `wwn-0x`, and `nvme-eui.` naming conventions.
- Construct recursive `pnfs_block_dev` trees for slices, concatenations, and stripes.
- Provide map callbacks (`bl_map_simple`, `bl_map_concat`, `bl_map_stripe`) that translate logical offsets to `struct block_device`, disk offset, and range length.
- Allocate and initialize `nfs4_deviceid_node` objects for the pNFS device cache.
- Free device-id nodes, close block-device files, and unregister SCSI persistent-reservation keys.

## Key Functions

- `bl_alloc_deviceid_node()` is the entry point from the pNFS device cache. It allocates a scratch folio, decodes all volumes from `pnfs_device` XDR pages, parses the last decoded volume as the top-level device, initializes the `nfs4_deviceid_node`, and marks it unavailable if parsing failed.
- `nfs4_block_decode_volume()` performs type-specific XDR decoding and bounds checks signature counts, signature lengths, volume counts, and SCSI designator lengths.
- `bl_parse_deviceid()` dispatches by volume type to simple, slice, concat, stripe, or SCSI parsing.
- `bl_parse_simple()` calls the pipefs/userspace resolver, opens the returned `dev_t`, records device length, and installs simple mapping.
- `bl_parse_scsi()` validates binary EUI64/NAA designators, opens a by-id path, validates nonzero length and persistent-reservation support, then stores the PR key.
- `bl_register_dev()` and `bl_unregister_dev()` recurse through device trees and register/unregister persistent-reservation keys only for leaf SCSI devices.
- `bl_free_deviceid_node()` tears down the recursive device tree and releases the enclosing cache node with RCU.

## Control Flow and State

The server supplies a flat array of volumes, where composite volumes reference earlier entries by index. `bl_alloc_deviceid_node()` decodes the array, then calls `bl_parse_deviceid()` on `nr_volumes - 1`, treating the final volume as the root. Composite parsers allocate child arrays, recursively parse referenced child volumes, and accumulate length/start metadata. The map callbacks later walk this tree to answer I/O mapping requests.

SCSI registration state is tracked with `PNFS_BDEV_REGISTERED` in `pnfs_block_dev::flags`. Registration is idempotent through `test_and_set_bit()`, and failure during recursive registration unwinds already registered children.

## Integration Points

- Uses `blocklayout.h` data structures and constants for volume/device layout.
- Calls `bl_resolve_deviceid()` from `rpc_pipefs.c` for simple signature-to-device resolution.
- Uses the NFS device-id cache through `nfs4_init_deviceid_node()`, `nfs4_mark_deviceid_unavailable()`, and RCU node freeing.
- Emits pNFS blocklayout tracepoints such as PR key registration/unregistration events.
- Uses block-layer APIs `bdev_file_open_by_dev()`, `bdev_file_open_by_path()`, `file_bdev()`, and persistent-reservation `pr_ops`.

## Concurrency and Lifetime

The file relies on the device-id cache for publication and RCU lifetime. Leaf devices own `struct file *bdev_file` references and release them with `fput()`. Composite devices own child arrays. Persistent-reservation registration is tracked per leaf device and unwound during free. Parsing failure may still return an initialized device-id node marked unavailable, allowing the cache to represent negative availability.

## Risks and Edge Cases

- Composite volume parsing assumes referenced indexes are valid; this file bounds volume counts but does not visibly validate every reference index against `nr_volumes`.
- `bl_parse_concat()` and `bl_parse_stripe()` return immediately on child parse failure without locally freeing previously parsed children; cleanup depends on top-level device destruction paths if the partially built tree is retained.
- `bl_map_stripe()` sets `map->len` to the stripe chunk size after child mapping, so callers must still clip to requested I/O ranges and device boundaries.
- SCSI path resolution is distribution- and udev-name-dependent; the fallback sequence is explicit and may fail if by-id links are unavailable.
- Persistent reservations require block-device support for `pr_ops`; unsupported devices are rejected.

## Testing Focus

Useful tests or review cases include malformed XDR for each volume type, invalid SCSI designator lengths/types, composite volumes with boundary index/count values, stripe offset mapping across child boundaries, PR registration unwind on partial failure, and unavailable-device cache behavior after parse failures.
