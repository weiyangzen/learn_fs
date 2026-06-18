# File Research: sources/virtualization/spdk/module/bdev/zone_block/vbdev_zone_block.c

Implements the `bdev_zoned_block` virtual bdev module, which presents a regular block bdev as a zoned block device with in-memory zone metadata.

Key elements:
- Registers `bdev_zoned_block` with init/fini/config/examine callbacks.
- Maintains pending config entries in `g_bdev_configs` and registered virtual devices in `g_bdev_nodes`.
- Models each zone with `struct block_zone`, `spdk_bdev_zone_info`, and a per-zone spinlock.
- Supports zone info, zone management, read, write, and zone append I/O.
- Enforces sequential write pointer semantics for writes and appends.
- Resets zones by updating in-memory state and optionally issuing base-bdev unmap.
- Creates virtual bdevs when the base bdev appears during examine or RPC-driven creation.
- Handles base bdev hotremove by unregistering dependent virtual bdevs.

Dependencies:
- SPDK bdev module APIs, bdev zone API, UUID generation, JSON config output, IO channel APIs.
- `vbdev_zone_block.h` exposes create/delete entry points used by RPC code.

Research notes:
- The wrapper does not persist zone state; zones initialize as full with write pointer at zone end.
- Zone size is rounded up to a power of two from `zone_capacity`; indexing uses `zone_shift`.
- Some base-bdev capacity may be truncated when it does not align to virtual zone layout.
- `GET_ZONE_INFO` is handled internally, but `zone_block_io_type_supported()` does not advertise `SPDK_BDEV_IO_TYPE_GET_ZONE_INFO`, which is notable.
