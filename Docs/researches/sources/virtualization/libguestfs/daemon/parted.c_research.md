# File Research: sources/virtualization/libguestfs/daemon/parted.c

Partition table manipulation using `parted` and one `sfdisk` helper.

Important behavior:
- Normalizes supported partition table aliases through `check_parttype`.
- Calls `udev_settle` before and after partition table mutations.
- Implements label creation, partition add/delete/resize, whole-disk single partition creation, boot flag set/get, GPT name set/get, and MBR ID setting.
- Uses `parted -s --` for mutations and `parted -m -s ... unit b print` for parsing.
- `do_part_disk` uses 128-sector alignment and leaves 128 sectors at disk end.
- `print_partition_table` maps unrecognized disk labels to `EINVAL`.
- `get_table_field` parses colon/semicolon-delimited machine output.

Filesystem relevance: block-device partition topology setup for filesystems and virtual disks.
