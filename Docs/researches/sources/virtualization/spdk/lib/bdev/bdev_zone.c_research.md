# File Research: sources/virtualization/spdk/lib/bdev/bdev_zone.c

`bdev_zone.c` implements zoned-block-device helper APIs over the generic bdev I/O path.

Simple getters expose zone size, number of zones, zone-id calculation from an LBA, max zone append size, max open zones, max active zones, and optimal open zones. Zone-id calculation optimizes power-of-two zone sizes with a mask and otherwise uses integer division.

I/O helpers allocate a bdev I/O from the channel, populate zone-management or zone-append fields, initialize callback metadata with `bdev_io_init()`, and submit through `bdev_io_submit()`.

Supported operations are zone info retrieval, zone management action, zone append with optional metadata, vector zone append with optional metadata, and retrieval of append completion location from a completed bdev I/O.

Research notes: this file does not validate zoned capability itself; it assumes upper bdev layers and I/O submission validation enforce whether the target bdev supports the requested zoned operation.
