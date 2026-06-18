# File Research: sources/local-fs/btrfs-progs/cmds/filesystem-usage.h

## Purpose
Declares the shared device/chunk usage data model and helper API for filesystem and device usage commands.

## Types
- `struct device_info` stores devid, path, block-device size, and filesystem-occupied size.
- `struct chunk_info` stores grouped chunk type, size, devid, and number of stripes. Grouping is by `(type, devid, num_stripes)`.

## API
- `load_chunk_and_device_info()` populates arrays of `chunk_info` and `device_info`.
- `print_device_chunks()` and `print_device_sizes()` print device-level allocation details.
- `dev_to_fsid()` reads a device superblock and extracts fsid.
