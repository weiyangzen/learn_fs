# File Research: sources/local-fs/btrfs-progs/cmds/send.c

## Purpose

Implements `btrfs send`, producing a send stream for one or more read-only subvolumes through the kernel `BTRFS_IOC_SEND` ioctl. Handles full sends, incremental sends, clone sources, multi-subvolume stream framing, output files, no-data mode, and protocol version/compressed-data negotiation.

## Main Data Structure

`struct btrfs_send` tracks:

- send pipe fd and output fd
- mount fd
- clone source root IDs
- mount root path
- requested and supported protocol version

## Control Flow

1. `cmd_send()` parses options and output destination.
2. It resolves clone sources and parent subvolumes, ensuring they are read-only.
3. It verifies all target subvolumes are on the same Btrfs mount and read-only.
4. It detects kernel-supported send stream version via sysfs.
5. `--compressed-data` enforces protocol version >= 2 or auto-selects v2 if no protocol was explicitly requested.
6. For each target subvolume, `do_send()` opens it, creates a pipe, starts `read_sent_data()` to splice kernel stream data to output, and calls `BTRFS_IOC_SEND`.
7. Multi-subvolume `-e` mode omits stream headers/end commands as needed.

## Parent/Clone Logic

- `get_root_id()` resolves root id from path.
- `get_parent()` follows parent UUID metadata.
- `find_good_parent()` chooses a clone source matching the real parent lineage and closest creation transaction.
- Parent root id is also added as a clone source for explicit `-p`.

## Dependencies

Uses send-utils for subvolume UUID searches, path mount resolution helpers, sysfs feature probing, pthreads, splice/pipe/fcntl, and Btrfs ioctl definitions.

## Risks And Edge Cases

- `read_sent_data()` calls `exit(-ret)` from the helper thread on splice errors, terminating the whole process rather than returning cleanly.
- Clone source selection depends on UUID metadata and creation transactions; missing/stale metadata produces parent determination failures.
- `--proto 0` requests kernel default/highest behavior through versioned ioctl fields, while local validation only rejects some unsupported combinations.
- Output to a terminal is refused to avoid binary stream corruption.
