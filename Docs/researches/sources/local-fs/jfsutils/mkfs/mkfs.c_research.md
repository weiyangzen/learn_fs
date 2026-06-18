# File Research: sources/local-fs/jfsutils/mkfs/mkfs.c

Top-level `jfs_mkfs` formatter implementation. It parses command-line options, validates the device, creates or attaches a journal, lays out aggregate/fileset metadata, and writes superblocks last.

Command-line options:
- `-c`: verify blocks before building filesystem.
- `-O`: OS/2 compatibility/case-insensitive mode.
- `-q` or `-f`: quiet/no confirmation.
- `-V`: version only.
- `-j log_device`: external journal device.
- `-J device=...` or `-J journal_dev`: attach existing journal or create journal-only device.
- `-L vol_label`: set label.
- `-s log_size`: inline log size in MB.
- Optional trailing block count limits filesystem size.

Main flow:
- Rejects missing/extra args and invalid devices.
- Refuses to format mounted devices.
- Opens the device exclusively.
- Validates size against `MINJFS`.
- Prompts before destructive operations unless quiet.
- Formats external or internal journal via `jfs_logform`.
- Calls `create_aggregate(...)`.
- Flushes and closes device, then reports success/failure.

`create_aggregate(...)`:
- Reserves fsck workspace at the end of the aggregate.
- Initializes block allocation map.
- Clears reserved blocks and zeroes old primary/secondary superblocks first.
- Initializes primary aggregate inode map/table.
- Initializes secondary aggregate inode map/table after the block map.
- Creates the initial fileset.
- Optionally verifies blocks and records bad blocks.
- Writes the completed block map.
- Constructs the superblock, including AG size, log location/device, fsck workspace, UUID, label, flags, and secondary inode-map descriptors.
- Validates and writes primary and secondary superblocks last.

Notable issues:
- In `parse_journal_opts`, the UUID/LABEL open result handling appears inverted: it calls `fclose(log_fd)` when `log_fd == NULL`, which would be invalid.
- Uses `strcpy` into fixed `logdev[255]` for journal device strings.
- `volume_label` is fixed at 16 bytes and copied with `strncpy`.

Filesystem relevance: primary JFS filesystem creation utility and the central orchestrator for all mkfs metadata writers.
