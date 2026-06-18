# File Research: sources/local-fs/jfsutils/tune/tune.c

Implements `jfs_tune`, which lists or updates JFS filesystem/log superblock metadata.

Supported operations:
- `-l`: display filesystem or log superblock.
- `-L vol_label`: update volume/log label.
- `-U uuid`: set UUID to explicit UUID, `null`/`clear`, `time`, or `random`.
- `-J device=...`: attach an external journal to a filesystem.
- `-V`: version only.

Main behavior:
- Parses options and requires exactly one device.
- Opens read-only for listing, read/write for mutation.
- Refuses mutation on mounted filesystems; only `-l` is allowed when mounted.
- Tries primary filesystem superblock, then secondary filesystem superblock, then log superblock.
- Fixes a historical mkfs 1.0.18/1.0.19 external-journal version issue by updating filesystem version when safe.
- Updates both old `s_fpack` and newer `s_label` fields for filesystem labels.
- For UUID updates, bumps old filesystem superblock version to 2 so mount can recognize UUIDs.
- External journal attach validates the log superblock, copies log device number and UUID into the filesystem superblock, clears `JFS_INLINELOG`, and writes the updated superblock.

Notable bug:
- `EXIT(fd, rc)` expands to `fclose(fd); exit(rc);`, so it is only safe with valid open `FILE *`.

Filesystem relevance: controlled superblock/log-superblock metadata mutation and inspection utility.
