# File Research: sources/os/linux/linux/block/partitions/cmdline.c

Implements partition definitions supplied through the kernel command line via `blkdevparts=`.

Key responsibilities:
- Parses mtdparts-like definitions into block-device-specific partition lists.
- Supports explicit sizes, remainder size with `-`, optional start offsets with `@`, optional names in parentheses, and flags.
- Applies matching definitions by disk name.
- Emits partition metadata including volume name and read-only flag.
- Warns when command-line partitions overlap.

Important structures:
- `struct cmdline_subpart` stores name, byte offset, byte size, flags, and linked-list pointer.
- `struct cmdline_parts` stores a disk name and linked subpartition list.

Important functions:
- `parse_subpart()` parses one partition definition.
- `parse_parts()` parses one block-device definition.
- `cmdline_parts_parse()` parses the full semicolon-separated command line.
- `cmdline_parts_set()` maps byte ranges to sector-based partition entries.
- `cmdline_parts_verifier()` detects overlaps.
- `cmdline_partition()` is the parser entry point.
- `cmdline_parts_setup()` registers the `blkdevparts=` boot parameter.

Flags:
- `ro` maps to `ADDPART_FLAG_READONLY`.
- `lk` is parsed as `PF_POWERUP_LOCK` but not otherwise applied in this file.

Research relevance:
- This is the block partition path for fixed-layout embedded systems without on-disk partition tables.
