<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hlinkdb.py -->
# sources/sync-backup/bup/lib/bup/hlinkdb.py

## Purpose
This module stores the filesystem hard-link database used by saves to remember which archive paths correspond to the same `(dev, ino)` node.

## Important APIs, Types, And Functions
The public pieces are `pickle_load()`, `Error`, and `HLinkDB`. `HLinkDB` exposes `prepare_save()`, `commit_save()`, `abort_save()`, `add_path()`, `change_path()`, `del_path()`, and `node_paths()`.

## Control Flow
Construction loads a pickle map from node key (`b"dev:ino"`) to paths and builds the reverse path-to-node index. Mutations update both maps. `prepare_save()` serializes the node map to an `atomically_replaced_file` if non-empty, or schedules removal if empty. `commit_save()` closes the pending atomic replacement; `abort_save()` cancels it.

## State And Persistence Behavior
Persistent state is a pickle file at the provided path, usually `bupindex.hlink`. In-memory state is `_node_paths`, `_path_node`, `_pending_save`, and an `ExitStack` of cleanup callbacks. The class asserts closure in `__del__`.

## Dependencies And Integration Points
It depends on `pickle`, `atomically_replaced_file`, `fsync`, and `unlink`. `cmd/save.py` uses it with index metadata to detect hardlink targets and encode `Metadata.hardlink_target`.

## Risks And Edge Cases
The pickle format is trusted input from the local repository cache, so corruption or malicious content can raise or execute pickle semantics. `node_paths()` indexes directly and raises `KeyError` for unknown nodes. There appears to be an argument-order bug in `change_path()`: it calls `self.add_path(new_dev, new_ino, path)` but `add_path()` expects `(path, dev, ino)`, which would corrupt maps if exercised. Atomic save requires `prepare_save()` before `commit_save()` when data exists.

## Test Signals
Hardlink behavior is indirectly covered by save/restore and metadata tests such as `test/ext/test-save-restore`, `test/ext/test-meta`, and paths in `cmd/save.py` that call `hlink_db.node_paths()`. Focused tests should cover add/change/delete, empty-db unlink, abort cancellation, and pickle corruption.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hlinkdb.py -->
