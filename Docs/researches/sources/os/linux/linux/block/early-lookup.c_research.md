# File Research: sources/os/linux/linux/block/early-lookup.c

## Scope

This file resolves early-boot block device specifiers, especially root-device strings, before the root filesystem is mounted. It maps names, numeric device IDs, PARTUUID, and PARTLABEL strings to `dev_t`, and can print all known partitions for diagnostics.

## Core Lookup Paths

- `early_lookup_bdev()` dispatches accepted formats:
  - `PARTUUID=<uuid>[/PARTNROFF=<int>]`
  - `PARTLABEL=<name>`
  - `/dev/<disk-or-partition-name>`
  - hex encoded device number or `<major>:<minor>` numeric form.
- `devt_from_partuuid()` finds a block device by partition metadata UUID using `class_find_device()` and optionally applies `PARTNROFF`.
- `devt_from_partlabel()` finds a partition by GPT partition label.
- `devt_from_devname()` normalizes slashes to `!`, tries an exact disk name, then parses trailing decimal partition suffixes, including the `p<partno>` form for disk names ending in a digit.
- `devt_from_devnum()` accepts `<major>:<minor>`, a legacy three-field colon form, or hex-encoded `dev_t`.
- `blk_lookup_devt()` iterates `block_class` disk devices and resolves either whole-disk or partition `dev_t`.

## Diagnostics

- `bdevt_str()` formats small major/minor pairs as the historical root= hex format, otherwise as widened `major:minor`.
- `printk_all_partitions()` iterates visible non-empty disks and their xarray partition table under RCU, printing device number, size in KiB, `%pg` block-device name, partition UUID, and parent driver when available.

## Dependencies and Invariants

- Uses `block_class`, `disk_type`, `dev_to_disk()`, `dev_to_bdev()`, partition metadata, and `part_devt()`.
- PARTUUID matching is case-insensitive and prefix-length based on the parsed UUID portion.
- Invalid PARTUUID syntax is reported with a concrete expected format.
- This lookup is partition-table metadata lookup, not filesystem UUID lookup.
