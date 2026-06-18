# File Research: sources/virtualization/nbdkit/plugins/partitioning/partitioning.c

## Purpose
Implements the top-level `partitioning` plugin, which exposes multiple existing files as partitions inside one synthetic MBR or GPT disk.

## Main Entry Points
- `partitioning_load()` initializes region state, default GPT type GUID, and random state.
- `partitioning_config()` parses `file=`, `partition-type=`, `alignment=`, `mbr-id=`, and `type-guid=`.
- `partitioning_config_complete()` validates file count and chooses MBR or GPT when unspecified.
- `partitioning_get_ready()` calls `create_virtual_disk_layout()`.
- `partitioning_get_size()` returns the virtual disk size.
- `partitioning_pread()` maps reads across synthetic metadata, backing files, and zero padding regions.
- `partitioning_pwrite()` allows writes to backing file regions but rejects changes to partition metadata or nonzero writes to padding.
- `partitioning_flush()` fdatasyncs all backing files.

## Internal Mechanics
Each `file=` opens a backing file read-write, records its size and per-file partition attributes, and generates a random GPT unique GUID. The virtual disk is represented as a `regions` vector. Synthetic partition table regions are memory-backed, file partitions are fd-backed, and alignment padding is zero-backed.

## Dependencies
Uses POSIX file I/O, `device_size`, `fdatasync`, byte swapping, random helpers, common region/vector/GPT utilities, and nbdkit plugin API v2.

## Risks and Notes
All backing files are opened `O_RDWR` regardless of client readonly intent, so filesystem permissions must protect inputs. `total_size` accumulation does not visibly check uint64 overflow before MBR/GPT selection. The plugin advertises multi-conn safety while serving shared writable fds; this is reasonable for disjoint client coordination but still relies on clients avoiding conflicting writes to the same partitions.
