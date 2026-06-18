# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_sx.yaml

## Purpose
Baseline detailed DFS fixture for `SX` object class. It enumerates the small sample tree explicitly and is the reference for comparing RP_3GX and EC_16P2GX detailed fixtures.

## Important APIs, types, and functions
- Defines DFS superblock metadata akeys (`dfs_magic`, `dfs_sb_version`, `dfs_layout_version`, `dfs_chunk_size`, `dfs_obj_class`).
- Defines one `dfs_inode` array akey reused by directory entries.
- File objects use integer dkeys for metadata, full data chunks, and remainder chunks.
- `count` values reflect non-replicated SX logical layout.

## Control flow
The fixture is loaded by `read_yaml` and handed to `MetaOverhead`. It contains no behavior but drives estimator recursion exactly: one POSIX container, nine objects, and nested dkeys/akeys/values.

## State and persistence behavior
It models a single DFS namespace with explicit directory objects and regular-file data objects. Directory names and symlink target length contribute user/meta key sizes. Values larger than the SCM cutoff are counted toward NVMe by the estimator.

## Dependencies and integration points
This file anchors storage-estimator unit tests for filesystem exploration and YAML generation. It depends on exact key sizes, chunk size of 1 MiB, I/O size of 128 KiB, directory object class `S1`, and file object class `SX`.

## Risks and edge cases
The exact dkey counts are sensitive to chunking and remainder calculations. Symlink modeling has both inode-sized metadata and symlink target bytes in a single array akey. A typo or key-size mismatch can shift metadata totals without obvious YAML syntax errors.

## Test signals
Signals include successful parsing, stable estimator report totals for SX, and expected lower counts than replicated/EC fixtures for the same file tree.
