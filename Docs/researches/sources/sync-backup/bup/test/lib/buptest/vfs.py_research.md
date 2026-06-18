# sources/sync-backup/bup/test/lib/buptest/vfs.py

Purpose: independent VFS test helper that reads bup Git tree objects into dictionaries so tests can cross-check `bup.vfs` behavior without using the exact same traversal path.

Important APIs/types/functions: `TreeDictValue`, `tree_items(repo, oid)`, `tree_dict(repo, oid)`, `vfs.tree_data_and_bupm`, `vfs._FileReader`, `vfs.ordered_tree_entries`, `Metadata.read`, `BUP_CHUNKED`, `tree_entries`, and `S_ISDIR`.

Control flow: `tree_items()` fetches raw tree data and optional `.bupm` metadata object, opens a metadata reader if present, yields a synthetic `.` entry, orders Git entries in bupm-aware order, skips the `.bupm` entry itself, then yields directory entries with default or read metadata and file/symlink entries with read metadata. It closes the metadata reader in `finally`. `tree_dict()` materializes the iterator keyed by name.

State and persistence behavior: reads Git object data and metadata streams from a repo; no writes. Stream position in `.bupm` is significant because metadata records are consumed sequentially.

Dependencies/integration points: used by `test_resolve.py` and `test_vfs.py` as an oracle for saved tree contents. It intentionally shares low-level Git reading but avoids full VFS resolution to reduce common-mode test failures.

Risks and test signals: still depends on several `bup.vfs` internals, so it is not fully independent. Metadata EOF raises an explicit `EOFError` naming the entry, which is useful for detecting `.bupm` ordering or truncation bugs.
