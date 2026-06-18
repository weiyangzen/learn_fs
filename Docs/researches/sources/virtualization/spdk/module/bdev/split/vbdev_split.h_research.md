# File Research: sources/virtualization/spdk/module/bdev/split/vbdev_split.h

Header exposing split module control functions:
- `create_vbdev_split(base_bdev_name, split_count, split_size_mb)`.
- `vbdev_split_destruct(base_bdev_name)`.
- `vbdev_split_get_part_base(base_bdev)`.

It documents deferred creation behavior: configs can be added before the base bdev exists, and split bdevs are created during examination when the base appears.
