# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_vdev.c

## Purpose

`zpool_vdev.c` converts `zpool` command-line vdev arguments into the nvlist vdev tree passed to libzfs/kernel ZFS. It performs userland validation before pool create/add/split operations: syntax, device/file existence, in-use checks, replication consistency, ashift validation, whole-disk labeling, spare/cache/log/special/dedup handling, and final root-vdev construction.

## File Shape

- Size: 1,697 lines, 43,952 bytes.
- SHA-256: `50591ca6abd1fd855cc3fc5cc0408bc3a23509019386449813555334d260356b`.
- Public entry points in this file: `construct_spec()`, `split_mirror_vdev()`, and `make_root_vdev()`.
- Main local helpers: `make_leaf_vdev()`, `check_device()`, `check_disk()`, `check_slice()`, `check_file()`, `is_whole_disk()`, `get_replication()`, `check_replication()`, `make_disks()`, `is_device_in_use()`, `is_grouping()`, and `num_normal_vdevs()`.

## Core Behavior

- `make_leaf_vdev()` accepts full paths or `/dev/dsk` shorthand, distinguishes block devices from regular files, detects whole disks by probing the backup slice, records `ZPOOL_CONFIG_PATH`, `ZPOOL_CONFIG_TYPE`, `ZPOOL_CONFIG_IS_LOG`, optional allocation bias, optional `WHOLE_DISK`, optional `DEVID`, and optional `ASHIFT`.
- `is_grouping()` recognizes topological or class markers: `raidz`, `raidzN`, `mirror`, `spare`, `log`, `special`, `dedup`, and `cache`; it also enforces minimum and maximum child counts.
- `construct_spec()` walks the argv stream and builds a root nvlist with top-level children plus optional `SPARES` and `L2CACHE` arrays. It treats `log`, `special`, and `dedup` as allocation-class prefixes, supports mirrored class devices, and rejects duplicate `spare`, `log`, or `cache` grouping declarations.
- `check_slice()`, `check_disk()`, `check_device()`, and `check_file()` delegate in-use detection to libdiskmgt and libzfs, rejecting devices used by swap, active pools, reserved spares, or non-overridable consumers.
- `get_replication()` and `check_replication()` verify that new top-level vdevs are internally consistent and, when adding to an existing pool, compatible with the pool's current replication model. Logs are ignored for this consistency check, and raidz/mirror combinations are permitted only when their failure tolerance matches.
- `make_disks()` labels whole disks through `zpool_label_disk()`, rewrites the path to the selected pool slice, fills in a devid after labeling, recurses through children/spares/cache, and rejects boot-label creation on non-whole-disk or multi-vdev boot pools.
- `split_mirror_vdev()` optionally builds a target spec for `zpool split`, labels target disks unless dry-run, rejects grouping keywords as split devices, and calls `zpool_vdev_split()`.
- `make_root_vdev()` is the main validation pipeline: build spec, read current pool config if any, check device usage, check replication if requested, require at least one normal top-level vdev on create, optionally label whole disks, and return the completed root nvlist.

## Dependencies And Contracts

- Uses libnvpair nvlist schema keys from ZFS, including `ZPOOL_CONFIG_CHILDREN`, `TYPE`, `PATH`, `DEVID`, `WHOLE_DISK`, `IS_LOG`, `ALLOCATION_BIAS`, `NPARITY`, `ASHIFT`, `SPARES`, and `L2CACHE`.
- Uses libdiskmgt for in-use and overlap checks; failures from libdiskmgt are warnings except concrete in-use reports.
- Uses `zpool_in_use()`, `zpool_read_label()`, `zpool_label_disk()`, and `zpool_vdev_split()` from libzfs/libzutil-facing code.
- Relies on illumos device naming conventions under `ZFS_DISK_ROOT`, `ZFS_RDISK_ROOT`, and backup slice `s2`.

## Maintenance Notes

Changes here affect user-visible `zpool create`, `zpool add`, and `zpool split` validation behavior. Error wording is part of CLI ergonomics, and several checks are intentionally stricter than kernel acceptance to prevent accidental device reuse. Be careful with allocation-class state in `construct_spec()`: `log`, `special`, and `dedup` are sticky prefixes until another grouping/prefix resets them.
