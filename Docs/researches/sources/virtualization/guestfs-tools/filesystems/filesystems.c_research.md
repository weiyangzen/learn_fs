# File Research: sources/virtualization/guestfs-tools/filesystems/filesystems.c

Implementation of `virt-filesystems`, a read-only inventory tool for guest filesystems, partitions, block devices, and LVM objects.

Major behavior:
- Creates a read-only libguestfs handle.
- Parses output selection options: `--filesystems`, `--extra`, `--parts`, `--blkdevs`, `--lvs`, `--vgs`, `--pvs`, `--all`.
- Supports output shaping: `--long`, `--csv`, `--human-readable`, `--uuid`, `--fs-version`, `--no-title`.
- Requires at least one `-a` or `-d` drive source and rejects extra positional arguments.
- Launches libguestfs but does not mount an OS root for inspection.

Inventory paths:
- `do_output_filesystems`: uses `guestfs_list_filesystems`, filters `swap` and `unknown` unless `--extra`, canonicalizes devices, optionally probes label, UUID, FS version, size, and parents.
- `do_output_lvs`: lists logical volumes and derives VG parent from LV path.
- `do_output_vgs`: uses `guestfs_vgs_full`, emits VG UUID and resolves PV parents.
- `do_output_pvs`: caches `guestfs_pvs_full`, emits canonical PV paths.
- `do_output_partitions`: lists partitions, resolves parent block device, and optionally reads MBR IDs for msdos partition tables.
- `do_output_blockdevs`: lists block devices and RAID parents where applicable.

Output implementation:
- CSV mode writes rows immediately with local CSV quoting.
- Text mode buffers all rows, tracks max column widths, and prints aligned columns at the end.
- Empty fields render as `-` in text mode.
- Human-readable sizes use gnulib `human_readable`.

Notable details:
- RAID parent detection is a simple `/dev/md[0-9]+` test.
- VG parent resolution compares PV UUIDs while ignoring punctuation in `guestfs_vgpvuuids`.
- Filesystem size probing tries statvfs via temporary read-only mount when possible, otherwise falls back to block device size.
- XFS FS version support comes from local `get_filesystem_version`.

Research relevance: central guest storage topology reporting tool, useful for understanding libguestfs enumeration APIs and device relationship formatting.
