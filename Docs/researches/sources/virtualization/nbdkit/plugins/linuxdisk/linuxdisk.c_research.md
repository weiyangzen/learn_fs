# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/linuxdisk.c

This is the nbdkit plugin entry point for serving a host directory as an ext2/ext3/ext4 filesystem inside a GPT-partitioned virtual disk.

Configuration:
- Requires `dir`.
- Optional `label`.
- `type` defaults to `ext2` and must start with `ext`.
- `size` can be exact or `+SIZE` to add extra space to the estimated filesystem size.

Lifecycle:
- `linuxdisk_load` initializes the global virtual disk and seeds random state for partition GUID generation.
- `linuxdisk_get_ready` calls `create_virtual_disk`.
- `linuxdisk_unload` frees regions, GPT buffers, and temp fd.

NBD behavior:
- Reports size from the virtual region layout.
- Multi-connection is safe because the generated disk is read-only after creation.
- Cache is emulated by nbdkit through reads.
- `.pread` dispatches across region types: temp filesystem file, in-memory GPT/MBR data, or zero padding.

Integration:
- Uses `filesystem.c` to create the ext filesystem.
- Uses `virtual-disk.c` for region layout.
- Uses `partition-gpt.c` for GPT structures.

Risks:
- Does not use `realpath` for `dir`, intentionally for external `mke2fs` path compatibility.
- Only a single `dir` is accepted.
- Source changes after `.get_ready` do not update the export.
