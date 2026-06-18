# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/pdisk.c

Implements the `pdisk` command-line entry point and interactive editor for Apple Partition Maps.

Key responsibilities:
- Parses `-l` list-only and `-r` read-only options.
- Opens the target disk as a character device using `opendev`.
- Verifies the device is a character device.
- Reads the OpenBSD disklabel and requires 512-byte sectors.
- Pledges to `stdio` after device setup.
- Opens an Apple partition map and either dumps it or enters interactive editing.
- Implements the interactive command loop and command dispatch.
- Prompts for partition base/length/name/type and map-editing parameters.
- Calls partition-map engine functions for create, delete, reorder, resize, rename, type change, display, and write.

Important functions:
- `main()` handles argument parsing, disk open/validation, disklabel checks, pledge, map loading, list/edit mode, cleanup, and exit.
- `edit()` prints command help and dispatches all interactive commands.
- `do_create_partition()` creates either a typed partition or the default OpenBSD partition type.
- `get_base_argument()` accepts a block number or `<n>p` partition-base modifier.
- `get_size_argument()` accepts a block count, byte multiplier, or `<n>p` partition-length modifier.
- `do_rename_partition()` and `do_change_type()` update DPME name/type fields and mark the map changed.
- `do_delete_partition()`, `do_reorder()`, `do_change_map_size()`, and `do_write_partition_map()` wrap corresponding map operations.
- `do_display_entry()` prints block zero or a full partition entry.
- `do_dump_map()` selects normal or verbose/internal dump output.
- `usage()` prints `usage: pdisk [-lr] disk`.

Interactive commands:
- `?` verbose help
- `h` command help
- `p` print partition map
- `P` show internal data structures
- `f` full display of one entry
- `i` reinitialize map
- `c` create an OpenBSD partition
- `C` create a partition with a specified type
- `d` delete
- `n` rename
- `t` change type
- `r` reorder entries
- `s` resize map
- `w` write
- `q` quit, prompting before discarding changes

Notable behavior:
- `-l` and `-r` both open the disk read-only; only `-l` automatically dumps instead of editing.
- Writes are blocked when `rflag` is set.
- Creating a partition with type `Apple_Free` or `Apple_partition_map` is rejected.
- Renaming clears the whole fixed-size DPME name buffer before copying the new string.
- Changing type clears with `memset` then copies the new type string and marks the map changed.
- Reinitialization creates a fresh default map only after user confirmation.

Dependencies:
- Uses `partition_map.h` for map operations and constants.
- Uses `io.h` for interactive input helpers.
- Uses `dump.h` for map and entry display.
- Uses OpenBSD disklabel, disk ioctl, device open, pledge, and `libutil` helpers.

Research notes:
- This file contains little partition logic itself; it is the user-interface shell over `partition_map.c`.
- Safety checks are mostly interactive confirmations and read-only/write-state gates, while structural map validation lives in `partition_map.c`.
