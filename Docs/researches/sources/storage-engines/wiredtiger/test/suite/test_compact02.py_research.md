# sources/storage-engines/wiredtiger/test/suite/test_compact02.py

Purpose: tests that compact reduces file size after deleting large records, and that dry-run mode records expected rewrite estimates without actual shrinkage expectations.

Important APIs and types: `compact_util`, manual `wiredtiger_open`, `session.compact`, `get_size`, `raisesBusy`, compact progress stats, and `make_scenarios`.

Control flow: open a connection with scenario cache size, create a table avoiding overflow values, insert alternating large/small records, checkpoint and measure size, delete all large records, checkpoint, compact with `free_space_target=1MB` and optional `dryrun=true` retrying `EBUSY`, then measure size and stats.

State and persistence behavior: after deletion, file free space should be reclaimable by foreground compaction unless dry-run is selected. Dry-run only estimates rewrite work.

Dependencies and integration points: directly controls connection setup to vary cache size, uses compact utility helper stats, and skips size assertions under tiered hook.

Risks: file-size thresholds depend on storage layout and avoiding overflow pages. Retry loop can take time under eviction conflicts.

Test signals: non-dry-run non-tiered size falls below half full size and progress stats reconcile reviewed/rewritten/skipped pages; dry-run with enough pages reports expected bytes/pages.
