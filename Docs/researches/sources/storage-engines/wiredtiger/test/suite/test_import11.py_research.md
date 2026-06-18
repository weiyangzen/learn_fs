# sources/storage-engines/wiredtiger/test/suite/test_import11.py

Purpose: tests tiered-storage import using an exported metadata file (`WiredTiger.export`) and rejects incompatible `file_metadata` import forms for tiered tables.

Important APIs and functions: this file defines its own `test_import_base` mixing `TieredConfigMixin` with `WiredTigerTestCase`. Helpers include timestamped `update/delete/check`, `populate`, file-copy helpers, and `checkpoint_and_flush_tier`. `test_import11` uses `gen_tiered_storage_sources`, `backup:export`, `tiered_conn_config`, and import success/failure statistics.

Control flow: it creates and populates two tiered tables, opens `backup:export` to produce `WiredTiger.export`, copies the export file into `IMPORT_DB`, reopens there, populates unrelated data, advances oldest timestamp, copies local/bucket/cache-bucket files, validates that `file_metadata` import configs fail in tiered scenarios and increment failure stats, then imports both tables with `metadata_file="WiredTiger.export"`, checkpoint/flushes after each, checks success stats, removes the export file, validates imported values, writes remaining rows, and checkpoints.

State and persistence behavior: tiered import state spans local files, bucket data, cache-bucket data, and an export metadata file. `file_metadata` is intentionally incompatible with this mode.

Dependencies and integration points: integrates tiered hooks, backup export, object-store-like directory layout, import stats, and timestamp validation.

Risks and edge cases: the source contains a likely bug while reading metadata (`table_config = cursor[k]` uses `cursor`, not `meta_c`). This path only matters inside the tiered invalid-config block and may raise `NameError` before the intended assertions. Verification is disabled for tiered storage with a FIXME.

Test signals: invalid tiered configs increment import-fail stats; both valid imports increment success stats; imported values are readable and post-import writes work.
