# sources/storage-engines/leveldb/db/recovery_test.cc

Purpose: exercises DB recovery behavior around MANIFEST reuse, large MANIFEST compaction, missing logs, log reuse, multi-log recovery, and missing descriptor files. The fixture opens a temporary DB with `reuse_logs` by default and exposes helpers for direct file inspection and synthetic log creation.

Important APIs and functions: `RecoveryTest::OpenWithStatus`, `Open`, `Close`, `Put`, `Get`, `CompactMemTable`, `ManifestFileName`, `RemoveLogFiles`, `RemoveManifestFile`, `GetFiles`, `MakeLogFile`, and the test cases `ManifestReused`, `LargeManifestCompacted`, `NoLogFiles`, `LogFileReuse`, `MultipleMemTables`, `MultipleLogFiles`, and `ManifestMissing`.

Control flow: the fixture repeatedly closes and reopens `DBImpl`, compares filesystem state before and after recovery, and injects additional log records through `log::Writer` plus `WriteBatchInternal`. `MultipleMemTables` reduces `write_buffer_size` so recovery must flush multiple memtables into tables rather than reusing the old log. `MultipleLogFiles` appends newer numbered logs, checks they are recovered once, and verifies a stale older log is ignored later.

State and persistence behavior: the tests are centered on persistent files named by `filename.h`: `CURRENT`, MANIFEST/descriptor, log files, and table files. They verify that small appendable manifests and empty logs can be reused, oversized manifests are rewritten compactly, missing logs lose unflushed writes, and a missing MANIFEST is reported as corruption or Chromium-specific I/O error.

Dependencies and integration: depends on `DBImpl` test hooks, `VersionSet` naming conventions, `WriteBatchInternal` log record layout, `Env`, `log::Writer`, and test utilities. It is a regression harness for `VersionSet::Recover`, `ReuseManifest`, and DB open logic.

Risks and edge cases: tests branch on append support because not all `Env` implementations can reopen files appendably. Direct log injection must keep sequence numbers coherent. The `Get` helper accepts a snapshot argument but does not pass it into `ReadOptions`, so snapshot behavior is not covered here.

Test signals: strong signals for recovery/open idempotence, manifest size thresholds, log-number monotonicity, and stale-log exclusion. It does not test corrupted records in detail or all `reuse_logs=false` paths.
