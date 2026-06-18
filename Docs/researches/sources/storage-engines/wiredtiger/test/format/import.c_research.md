# sources/storage-engines/wiredtiger/test/format/import.c

Purpose: runs a background import workload that repeatedly imports a simple table file from a secondary database into the main format home, validating import metadata, repair, dry-run-like alter/drop/reimport, and fallback repair behavior.

Important APIs and functions: `import`, `populate_table`, `verify_import`, `get_file_metadata`, and `copy_file_into_directory`. WiredTiger APIs include `create`, `checkpoint`, `alter`, metadata cursor reads, `drop(remove_files=false)`, `open_cursor`, and internal `__wt_copy_and_sync`.

Control flow: creates `g.home/IMPORT`, opens a separate connection, creates and populates `table:import` with 1,000 integer key/value pairs, captures table and file metadata, then until workers finish copies `import.wt` to the parent home and chooses one of several import modes: repair-only, metadata import, or import/checkpoint/alter/checkpoint/drop-keep-file/reimport with possible repair fallback. Every import is verified and dropped before sleeping.

State and persistence: creates a secondary WiredTiger database and repeatedly copies/imports `import.wt` into the main home. It depends on persistent metadata strings for `table:import` and `file:import.wt`, and intentionally leaves the source import database stable across iterations.

Dependencies and integration: spawned by `operations` when `GV(IMPORT)` is set. It uses `create_database` from `wts.c`, main `g.wts_conn`, testutil drop helpers, and global extra RNG. It runs concurrently with other workload threads.

Risks and test signals: metadata strings must remain valid after retrieval; forced checkpoints can make non-repair reimport fail, which is expected only before fallback. Verification asserts every key/value equals its ordinal and exactly 1,000 entries exist; failures identify import corruption, metadata mismatch, or copy/sync bugs.
