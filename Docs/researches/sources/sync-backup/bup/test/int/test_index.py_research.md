# sources/sync-backup/bup/test/int/test_index.py

Purpose: exercises bup index creation, index metadata storage, merge ordering, dirty/valid flags, parent resolution, and support for negative filesystem timestamps.

Important APIs/types/functions: `index.MetaStoreWriter`, `index.Writer`, `index.BlankNewEntry`, `index.merge`, `metadata.empty_metadata`, `xstat.stat`, `resolve_parent`, local helpers `dump()`, `fake_validate()`, and `eget()`.

Control flow: `test_index_basic()` checks `resolve_parent()` versus `realpath()` for sample data and symlinks. `test_index_writer()` writes several file and directory entries to a temporary index. `test_index_negative_timestamps()` creates a file, assigns pre-epoch timestamps, updates a blank entry from stat data, and asserts it packs. `test_index_dirty()` creates three partial indexes, reads them before close, compares reader ordering, merges them, validates selected entries, and checks invalidation propagation to ancestors.

State and persistence behavior: creates temporary index and metadata files, changes CWD, stores metadata offsets, and mutates packed index entry validity flags. It intentionally works with not-yet-closed writers through `new_reader()` to validate live index state.

Dependencies/integration points: integrates filesystem stat wrappers, bup index binary serialization, metadata offset storage, merge conflict rules, fake SHA validation, and path parent resolution used by indexing commands.

Risks and test signals: relies on old negative timestamp support in the host filesystem. Merge order and invalidation expectations are exact byte-path lists. Failures reveal broken path sorting, metadata offset handling, dirty-entry propagation, or inability to serialize pre-1970 timestamps.
