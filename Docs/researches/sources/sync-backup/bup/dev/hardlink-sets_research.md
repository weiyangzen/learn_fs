# sources/sync-backup/bup/dev/hardlink-sets

## Purpose
Lists hardlink groups beneath supplied paths, one group per block, for restore/index validation.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `get_argvb`, `os.walk`, `os.lstat`, `st_dev/st_ino`, and `byte_stream`.

## Control Flow
Builds a map from device/inode to full byte paths for all non-directory files, sorts paths within each group and groups by first path, and prints only groups with more than one path separated by blank lines.

## State and Persistence Behavior
Read-only traversal; no persistence.

## Dependencies and Integration Points
Used by tests checking hardlink preservation across save/restore.

## Risks and Test Signals
Risks include concurrent filesystem mutation and hardlink semantics across filesystems. Signal is deterministic sorted byte-path grouping.
