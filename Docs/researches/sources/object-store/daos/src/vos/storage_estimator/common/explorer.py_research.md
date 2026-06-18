# sources/object-store/daos/src/vos/storage_estimator/common/explorer.py

## Purpose
Models filesystem contents as DAOS DFS/VOS storage-estimator structures. It can build detailed structures from an actual directory walk or average structures from aggregate counts and sizes.

## Important APIs, Types, And Functions
`FileInfo` and `Entry` abstract Python version differences in directory entries. `CellStats` tracks payload/parity cells. `DFS` builds `VosObject`/`DKey`/`AKey` representations for directories, files, symlinks, replicated data, and erasure-coded layouts. `AverageFS` creates a summarized DFS model from counts/averages. `FileSystemExplorer` walks the filesystem, collects stats, and exposes detailed or average DFS models.

## Control Flow
`FileSystemExplorer.explore` resets stats, enqueues the root, creates one directory object per visited directory, and processes entries with `os.scandir` on Python 3.5+ or `os.listdir` fallback. File entries add metadata to the current directory object and create file data objects. Directories enqueue traversal. Symlinks add inode values sized by link length. `DFS.create_file_obj` splits file sizes by chunk, IO size, object class replication/parity, EC cell size, and optional aggregation assumption.

## State And Persistence
All structures are in memory until callers dump YAML. Explorer state tracks queue, counts, sizes, current object id, and generated `DFS`. No persistent writes occur in this module.

## Dependencies And Integration
Depends on `storage_estimator.util.ObjectClass/CommonBase` and `vos_structures`. Consumed by CLI commands for `explore_fs`, CSV processing through `AverageFS`, and tests.

## Risks
There are user-visible typo/debug issues (`Gloabal`, swapped labels in `print_stats`, `self.dfs` instead of `_dfs` in `set_dfs_file_meta`). Empty directories remove the just-created object. EC math has several branches where edge cases around partial chunks/cells should be regression-tested. Directory traversal follows real paths for queued directories, which may collapse symlinked paths.

## Test Signals
`FSTestCase` builds a mock filesystem and compares aggregate object/dkey/akey/value stats for SX, RP_3GX, and EC_16P2GX classes. More direct tests should cover zero-length files, empty directories, symlinks, permission errors, EC partial chunks, and average model calculations.
