# File Research: sources/local-fs/btrfs-progs/cmds/device.c

## Purpose
Implements `btrfs device` subcommands for adding/removing devices, scanning/forgetting devices, readiness checks, IO stats, per-device usage, and the replace alias.

## Device Mutation Commands
- `cmd_device_add()` validates target devices, checks exclusive-operation state, rejects host-managed zoned devices for non-zoned filesystems, prepares devices with optional discard, canonicalizes paths, and calls `BTRFS_IOC_ADD_DEV`.
- `_cmd_device_remove()` backs both `remove` and `delete`; it supports device paths, numeric devids, `missing`, and `cancel`, uses `BTRFS_IOC_RM_DEV_V2`, and falls back to legacy `BTRFS_IOC_RM_DEV` only when compatible.
- Multiple removals warn and delay unless `--force` is used.

## Scan and Ready
- `btrfs_forget_devices()` calls `/dev/btrfs-control` with `BTRFS_IOC_FORGET_DEV`.
- `cmd_device_scan()` scans all devices, specified block devices, or forgets stale/specified devices.
- `cmd_device_ready()` canonicalizes a block device and calls `BTRFS_IOC_DEVICES_READY` through `/dev/btrfs-control`.

## Device Stats
- `cmd_device_stats()` supports mounted ioctl reads and `--offline` reads from the dev tree.
- Online mode opens the mount and calls `BTRFS_IOC_GET_DEV_STATS`, optionally with reset.
- Offline mode opens ctree state and uses `get_device_stats_offline()` to read `BTRFS_DEV_STATS_OBJECTID` persistent items.
- Output supports plain text, JSON, and tabular `-T`; `--check` returns bit `64` if any counter is nonzero.

## Device Usage
- `_cmd_device_usage()` loads chunk/device info via `load_chunk_and_device_info()` and prints per-device sizes plus chunk allocation details using helpers from `filesystem-usage.c`.

## Registration
Registers add, delete alias, remove, replace alias, scan, ready, stats, and usage under the `device` group.
