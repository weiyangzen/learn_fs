# File Research: sources/virtualization/spdk/module/bdev/raid/Makefile

This Makefile builds the SPDK RAID bdev module as library `bdev_raid`.

It sets `SPDK_ROOT_DIR`, includes SPDK common make rules, sets shared object version `8.0`, adds `lib/bdev` to the include path, and compiles `bdev_raid.c`, `bdev_raid_rpc.c`, `bdev_raid_sb.c`, `raid0.c`, `raid1.c`, and `concat.c`. When `CONFIG_RAID5F=y`, it also includes `raid5f.c`. The module uses `mk/spdk_blank.map` and common SPDK library rules.
