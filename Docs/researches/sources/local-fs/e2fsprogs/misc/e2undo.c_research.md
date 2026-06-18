# File Research: sources/local-fs/e2fsprogs/misc/e2undo.c

## Purpose
Implements `e2undo`, which validates and replays e2fsprogs undo logs back onto an ext2/3/4 filesystem or image.

## Undo Format
- Header block begins with magic `E2UNDO02`.
- Header records number of keys, superblock copy offset, key block offset, undo block size, filesystem block size, superblock CRC, state, feature flags, and optional filesystem offset.
- Key blocks begin with `KEYBLOCK_MAGIC` and contain `undo_key` entries mapping filesystem block numbers to data blocks in the undo file.
- Each data block/extent has a CRC.

## Main Behaviors
- Parses `-f`, `-h`, `-n`, `-o`, `-v`, and `-z`.
- Refuses to use the replayed undo file as the new backup undo file.
- Opens and validates the undo file header, feature flags, block sizes, and CRCs unless forced.
- Refuses mounted target filesystems.
- Optionally wraps target writes with undo I/O manager for a new undo file.
- Applies filesystem offset from command line or undo file feature.
- Compares target superblock with undo file’s saved superblock unless forced.
- Reads all key blocks, verifies key block CRCs and individual block CRCs.
- Sorts replay keys by target filesystem block.
- Replays data to target unless dry-run.
- If corruption/I/O/incomplete undo state is detected, marks the target filesystem invalid and possibly errored to force fsck.

## Important Functions
- `dump_header`: prints undo header metadata.
- `print_undo_mismatch`: explains superblock mismatches.
- `check_filesystem`: verifies the undo file matches current target filesystem state and saved superblock CRC.
- `key_compare`: orders replay by filesystem block.
- `e2undo_setup_tdb`: configures undo I/O manager and selects backup undo file path.

## Dependencies
- ext2fs I/O managers, undo I/O manager, CRC32C, filesystem open/close.
- POSIX path and environment helpers.
- `E2FSPROGS_UNDO_DIR`, defaulting to `/var/lib/e2fsprogs`.

## Notes and Edge Cases
- `-h` in code dumps the undo header and exits with status `1`, while the manpage calls it a usage message.
- `-f` allows operation through checksum and feature problems but tracks corruption/I/O warnings.
- Maximum replay extent size is capped at `512 * undo block size`.
