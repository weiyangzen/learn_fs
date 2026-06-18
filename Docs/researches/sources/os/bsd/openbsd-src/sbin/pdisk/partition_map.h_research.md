# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.h

Declares the Apple Partition Map data model and public partition-map API for `pdisk`.

Key contents:
- Defines Apple block-zero and DPME signatures:
  - `BLOCK0_SIGNATURE` as `0x4552` (`ER`)
  - `DPME_SIGNATURE` as `0x504D` (`PM`)
- Defines `DPISTRLEN` as the 32-byte Apple partition name/type string length.
- Defines `struct ddmap`, the block-zero driver descriptor entry.
- Defines `struct partition_map`, including:
  - disk-order and base-order entry lists
  - device name and file descriptor
  - changed flag
  - map capacity/count fields
  - media size
  - block-zero fields and driver descriptor array
- Defines `struct entry`, including:
  - list links for both orderings
  - parent map and disk address
  - DPME on-disk fields
  - NUL-extended partition name/type strings
  - partition flags, boot fields, checksum, processor ID, and reserved data
- Defines DPME flag bits such as valid, allocated, in-use, bootable, readable, writable, and OS-specific flags.

Exported symbols:
- Partition type strings: `kFreeType`, `kMapType`, `kUnixType`, and `kHFSType`.
- Global mode flags from `pdisk.c`: `lflag` and `rflag`.
- Map creation/loading: `create_partition_map()`, `open_partition_map()`.
- Entry lookup: `find_entry_by_disk_address()`, `find_entry_by_type()`, `find_entry_by_base()`.
- Mutation: `add_partition_to_map()`, `delete_partition_from_map()`, `move_entry_in_map()`, `resize_map()`.
- I/O/lifecycle: `write_partition_map()`, `free_partition_map()`.
- Helpers: `contains_driver()`, `dpme_init_flags()`.

Dependencies:
- Requires `sys/queue.h`-style `LIST_HEAD` and `LIST_ENTRY`.
- Uses fixed-width integer types.

Research notes:
- This header mirrors Apple Partition Map on-disk layout closely, including fixed reserved-field sizes.
- It is the boundary between the interactive editor, dump code, I/O code, and partition-map mutation engine.
