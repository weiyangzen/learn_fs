<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/__init__.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/__init__.py

Purpose: shared helper module for chunker tests, especially sparse-file fixtures and chunk result normalization.

Important APIs/functions: `cf`, `cf_expand`, `make_sparsefile`, `make_content`, `fs_supports_sparse`, constants `BS`, `map_sparse1`, `map_sparse2`, `map_notsparse`, and `map_onlysparse`.

Control flow: `cf` maps chunk objects into either bytes for `CH_DATA` or integer lengths for `CH_HOLE`/`CH_ALLOC`, while asserting metadata/data consistency. `cf_expand` turns hole/allocation integers into zero bytes for reconstruction tests. Sparse helpers create real sparse files or expected content maps from `(offset, size, is_data)` triples. `fs_supports_sparse` creates a temporary sparse file and probes `SEEK_HOLE`/`SEEK_DATA`.

State and persistence: helper creates temporary or named files and uses filesystem sparse capabilities; maps describe block-level sparse layouts.

Dependencies/integration: used by fixed, buzhash, reader, and self-test modules. Depends on constants `CH_DATA`, `CH_HOLE`, `CH_ALLOC`, `BS`, and `has_seek_hole`. Risks are assuming block-size alignment and OS coalescing behavior. Test signals are assertions inside helpers and sparse capability return value.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/__init__.py -->
