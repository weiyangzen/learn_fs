# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_bdev.c

Management helpers for opening, validating, claiming, and closing base and NV-cache bdevs.

Base bdev handling:
- Opens by name read/write, claims through dummy `ftl_lib` module, validates 4 KiB block size and minimum 20 GiB capacity.
- Creates IO channel, derives transfer size, validates power-of-two xfer size, selects base device type, records metadata size, requires metadata layout ops, rejects zoned devices, initializes base layout tracker.
- Cleanup releases IO channel, bdev claim/descriptor, and layout tracker.

Cache bdev handling:
- Opens/claims by name, validates 4 KiB block size and minimum 5 GiB capacity, creates cache IO channel.
- Selects NV-cache device type, forces `nv_cache->md_size` to `sizeof(union ftl_md_vss)`, requires layout region creation ops, and initializes NV-cache layout tracker.
- Cleanup mirrors base close behavior.

Removal events currently assert, so hot-remove is not gracefully supported here.
