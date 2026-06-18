# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size01.py

Purpose: validates that disaggregated stable table checkpoint metadata includes a `size=` field and that it reflects compression, growth, and restart persistence.

Important APIs and control flow: `@disagg_test_class` runs a leader layered table. `conn_extensions` loads zstd and disaggregated extensions. `find_checkpoint_size` parses all `,size=N,` entries and returns the latest. Tests create `layered:` tables, write 1000 or 1500 rows, checkpoint, and read `metadata:` for `file:<uri_base>.wt_stable`.

State and persistence: stable table metadata is the ground truth. The restart test reopens after checkpoint and expects the checkpoint size to be unchanged.

Dependencies and integration: uses `DisaggConfigMixin`, disaggregated storage, zstd extension, metadata cursors, and checkpointing.

Risks and test signals: non-compressed size must exceed raw payload threshold; zstd-compressed size must be below it; second checkpoint must grow after more data. Failures indicate metadata size calculation or persistence regressions.
