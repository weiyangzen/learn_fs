# sources/storage-engines/wiredtiger/test/suite/test_checkpoint27.py

Purpose: checks that evicting metadata pages while reading checkpoint cursors does not corrupt checkpoint metadata access or history-store lookup.

Important APIs and types: `debug=(release_evict)` cursor on `file:WiredTiger.wt`, named/unnamed checkpoints, checkpoint cursor read timestamps, and `SimpleDataSet`.

Control flow: write two timestamped value generations, checkpoint, then repeatedly call `evict_metadata` before opening checkpoint cursors, after opening, and during first scan iteration. Reads are performed at historical timestamp 15, newer timestamp 25, default, no timestamp, and again at 15.

State and persistence behavior: the test forces metadata pages out of cache around checkpoint cursor reads so checkpoint handle/metadata reconstruction must be robust to eviction and reload.

Dependencies and integration points: directly touches the WiredTiger metadata file via an eviction debug cursor. Skipped for tiered and disaggregated hooks because checkpoint/metadata behavior differs.

Risks: metadata eviction is intentionally awkward and may be sensitive to metadata table size. Comments note preliminary scans may be required before metadata eviction reproduces the targeted path.

Test signals: all checkpoint scans return exactly expected values and counts, including historical reads that require history-store content.
