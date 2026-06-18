# File Research: sources/os/bsd/freebsd-src/sbin/growfs/growfs.c

`growfs.c` implements UFS filesystem growth for FreeBSD. It increases an existing UFS filesystem to a larger device or requested size by recalculating superblock fields, updating cylinder group metadata, and writing new summaries.

Key behavior:
- Parses `-N` dry-run, `-s size`, compatibility `-v`, and `-y` assume-yes.
- Resolves a device from either a special device path or a mounted filesystem using `getmntpoint()` and mount metadata.
- Reads the existing superblock via `sbget()`, rejects unclean filesystems, and copies old/new superblock state into separate globals.
- Defaults target size to provider size, or validates requested size suffixes `b`, `k`, `m`, `g`, `t`.
- Aligns target size to filesystem fragment size.
- Rejects shrink/no-op requests.
- Rejects active snapshots unless `-y` is used.
- Prompts before destructive growth unless `-y` or dry-run is used.
- If mounted read-write, uses `/dev/ufssuspend` and `UFSSUSPEND`/`UFSRESUME`; otherwise opens the device directly for writing.
- Tests read/write access to the new last filesystem fragment before modifying metadata.
- Recomputes `fs_size`, `fs_providersize`, UFS1 cylinder counts, `fs_ncg`, and `fs_cssize`.
- Drops an unusable final cylinder group if it lacks room for at least one data block.
- `growfs()` coordinates the actual metadata update:
  - Loads cylinder summaries.
  - Updates the former last cylinder group with new free fragments/blocks.
  - Initializes new cylinder groups.
  - Relocates cylinder summary storage when it grows.
  - Cleans dynamic superblock fields.
  - Writes the updated superblock with `sbput()`.
- `initcg()` creates a new cylinder group, initializes inode generation numbers, free block/fragment maps, cluster summaries, and cylinder summaries.
- `updjcg()` expands the old last cylinder group and updates free-space accounting.
- `updcsloc()` relocates cylinder summary data to the first newly created complete cylinder group when extra summary fragments are required.
- `frag_adjust()`, `updclst()`, `isblock()`, `setblock()`, and `clrblock()` manipulate UFS allocation maps and summary counters.
- `cgckhash()` recalculates cylinder-group CRC32C when metadata check hashes are enabled.

Important details:
- The source comments explicitly call out snapshot and crash-ordering limitations.
- Dry-run mode skips writes, but one branch notes it cannot fully simulate reading newly written cylinder-group data.
- The code supports both UFS1 and UFS2 layout differences.
