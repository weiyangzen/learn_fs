# sources/sync-backup/borg/src/borg/legacy/repository.py

Purpose: implements the filesystem-based legacy transactional repository. It stores object PUT/DELETE/COMMIT entries in numbered segment files, persists committed indexes/hints/integrity files, and handles rollback, replay, repair, and compaction.

Important APIs/types: `LegacyRepository` exposes create/open/close/destroy, config/key handling, transactions (`prepare_txn`, `commit`, `rollback`, `write_index`), checking/repair (`check`, `replay_segments`), compaction, and object access (`list`, `get`, `put`, `delete`, manifest helpers). `LoggedIO` owns segment iteration, CRC-checked reads, recovery, writes, and segment deletion. `NSIndex1` maps object IDs to segment/offset.

Control flow/state: writes prepare a transaction, load index and hints, append PUT/DELETE segment entries, update `index`, `segments`, `compact`, and `shadow_index`, then commit with a COMMIT tag and write side files. Opening reconciles index transaction IDs with last committed segment and can replay segments after interrupted commits. Compaction copies live PUTs, preserves necessary DELETEs using `shadow_index`, writes intermediate commits, deletes sparse segments, and rewrites the index.

Persistence: repository layout is `README`, `config`, `data/<dir>/<segment>`, `index.N`, `hints.N`, and `integrity.N`. Segment entries have magic, CRC32, size, tag, key, and optional data. `SaveFile`, `SyncFile`, fsyncs, and rename ordering provide durability best effort.

Dependencies/integration: used for local legacy repos and by `legacy.remote.RepositoryServer`. Integrates with `fslocking.Lock`, platform durability helpers, `IntegrityCheckedFile`, msgpack, progress indicators, and `Manifest.MANIFEST_ID`.

Risks: compaction crash windows and `shadow_index` correctness are central. Free-space estimates are conservative but filesystem-dependent. CRC32 is not cryptographic. Partial checks persist cursor state in config. Several invariants are assertion-based.

Test signals: transaction replay, corrupted hints/index, corrupted segment recovery, compaction preserving deletes, ENOSPC rollback cleanup, partial/full check, manifest missing mapping, and lock upgrade behavior.
