# File Research: sources/local-fs/xfsprogs/libxfs/topology.h

## Role

`topology.h` declares the userspace topology data structures and helpers used by mkfs/libxfs to derive filesystem geometry and to decide whether a target can be overwritten safely.

## Interface

- `struct device_topology` stores logical sector size, physical sector size, stripe unit, stripe width, and min/max atomic write unit values.
- `struct fs_topology` groups topology for data, realtime, and log devices.
- `libxfs_get_topology` fills an `fs_topology` from a `libxfs_init` device description.
- `calc_default_ag_geometry` computes data AG size/count defaults.
- `calc_default_rtgroup_geometry` computes realtime group size/count defaults.
- `check_overwrite` probes a device for existing signatures or partition tables.

## Notable Assumptions

The header is userspace-facing and does not define policy; all threshold logic, blkid probing, regular-file handling, and force-overwrite behavior live in `topology.c`.
