# File Research: sources/virtualization/spdk/module/bdev/raid/bdev_raid.h

This internal header defines the RAID bdev core data model, RAID-level module interface, I/O helpers, superblock format, and process option API used by all files in `module/bdev/raid`.

`struct raid_base_bdev_info` is the per-slot state for a base device: owning RAID, configured name/UUID, descriptor, data offset/size, removal/configuration callbacks, observed block count, app-thread channel, configured/process-target/failed flags, and removal scheduling state. `struct raid_bdev` is the RAID object: generic `spdk_bdev`, self descriptor, global list link, base slot array, strip geometry, state, base counts, RAID level, module pointer/private data, superblock buffers, active background process, and configure/destroy callbacks.

`struct raid_bdev_io` is the per-front-end-I/O context stored in SPDK bdev I/O driver context. It tracks logical offset/length, iovs, type, memory domain, metadata, wait queue entry, RAID channel, child completion counters/status, module-private data, optional custom completion, and split-state used when an active process divides an I/O into processed and unprocessed ranges.

The RAID-level module contract is `struct raid_bdev_module`. Each module declares its RAID level, minimum base count, optional base-removal tolerance constraint, memory-domain and DIF support flags, and callbacks for `start`, optional asynchronous `stop`, read/write submission, optional null-payload submission, optional module I/O channel, optional resize, and process request submission. `RAID_MODULE_REGISTER()` installs a module at constructor time.

The header declares core lifecycle APIs for create/delete/add/remove/find, string conversions, info JSON writing, module registration, I/O completion and queue helpers, channel accessors, process request completion, I/O initialization, and base-failure signaling. Inline wrappers for read/write/unmap/flush add each base slot's `data_offset`; the write wrapper also remaps DIX reference tags when enabled.

The superblock layout is fixed-size-header plus variable base array. The signature is `SPDKRAID`, version is `1.0`, the base member record is statically asserted to 64 bytes, and the header to 256 bytes. The maximum superblock length is constrained to fit below the minimum 1 MiB RAID data offset. Base superblock states include missing, configured, failed, and spare. Public superblock helpers allocate/free/init/write/clear/read superblocks.

`struct spdk_raid_bdev_opts` exposes background process tunables: process window size in KiB and max bandwidth in MiB/sec. `raid_bdev_get_opts()` and `raid_bdev_set_opts()` are used by the RPC layer and config JSON.
