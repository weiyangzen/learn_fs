# sources/sync-backup/borg/docs/usage/recreate.rst.inc

Purpose: Documents `borg recreate`, a dangerous archive rewriting command used to filter paths, change metadata/comment/timestamp/compression, or rechunk existing archives.

Important APIs/types/functions: CLI contract is `borg [common options] recreate [options] [PATH...]`. Important options include `--list`, `--filter`, `--dry-run`, `--stats`, include/exclude controls, archive filters, `--target`, `--comment`, `--timestamp`, `--compression`, and `--chunker-params`.

Control flow: Runtime selects archives, applies archive-relative path/pattern filtering, builds replacement archives as `<ARCHIVE>.recreate`, then removes/replaces the original after successful completion unless `--target` creates a separate new archive.

State and persistence: Mutates archive metadata and contents by creating new archive IDs and potentially deleting files from archives permanently. Old data is not physically freed until `borg compact`; rechunking can temporarily require substantial additional deduplicated space.

Dependencies and integration points: Shares pattern semantics with create but applies them to archived paths, not the local filesystem. Integrates with compression, chunker parameters, archive filters, stats/list status output, and repository compaction.

Risks: High data-loss risk if patterns are wrong. Absolute paths do not match because archive paths are relative. Rechunking after missing chunks can be unsafe; docs recommend recreating missing chunks with another backup/check first.

Test signals: Cover dry-run/list interpretation, target-vs-replace behavior, archive ID changes, path filtering, exclude tags, compression and chunker changes, stats output, interrupted recreate cleanup, and missing chunk scenarios.
