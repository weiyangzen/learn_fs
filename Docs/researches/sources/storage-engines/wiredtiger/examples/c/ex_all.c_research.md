# sources/storage-engines/wiredtiger/examples/c/ex_all.c

Purpose: broad API sampler used to populate WiredTiger API reference snippets and to compile/run representative calls across connection, session, cursor, transaction, statistics, packing, checkpoint, extension, checksum, and version APIs.

Important APIs and control flow: `main` opens a logged, statistical connection, then `connection_ops` registers a sample collator, reconfigures eviction, validates configuration, configures method-specific options, opens a session, and closes the connection. `session_ops` creates/drops tables with multiple storage options, alters/compacts/salvages/truncates/verifies, checkpoints, and delegates to `cursor_ops`, `cursor_statistics`, `pack_ops`, and `transaction_ops`. Cursor examples cover metadata/statistics cursors, duplicate cursors, overwrite configuration, named checkpoints, comparison/equality, append record numbers, reserve, modify, update, remove, and error reporting. Transaction examples cover commit/rollback, isolation, prepare/commit timestamps, reset_snapshot, pinned range, timestamp setters, query_timestamp, and rollback_to_stable.

State and persistence: creates many temporary tables in WT_HOME, writes records, checkpoints, changes connection/session settings, registers an in-process collator, and manipulates timestamps. Several documentation-only extension/compression examples are excluded by `MIGHT_NOT_RUN`.

Dependencies and integration: depends on public WiredTiger APIs, `test_util.h`, documentation snippet markers, and the `wt` build environment. The collator and method-configuration snippets show extension integration patterns.

Risks: because it is a snippet aggregator, call ordering is fragile; earlier table creation and inserted keys are prerequisites for later cursor operations. Some examples intentionally reference nonportable paths or unavailable extensions behind preprocessor guards. Timestamp examples require valid transaction sequencing.

Test signals: successful execution without assertion validates that documented snippets remain compileable and mostly runnable. Documentation extraction should preserve all `/*! [...] */` regions.
