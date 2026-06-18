# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/backupdb.py

## Purpose
Implements the SQLite cache used by `tahoe backup` to avoid re-uploading unchanged files and re-creating identical immutable directories. It records local file metadata, caps, upload/check timestamps, and directory content hashes.

## APIs, Types, And Control Flow
`get_backupdb` opens or creates the database with schema v2 and returns `BackupDB_v2`. `FileResult` and `DirectoryResult` are callback handles used by backup code to report successful uploads/checks. `BackupDB_v2.check_file` stats the absolute path, compares size/mtime/ctime unless timestamps are ignored, retrieves the previous cap, and probabilistically decides whether to re-check health based on `NO_CHECK_BEFORE` and `ALWAYS_CHECK_AFTER`. `check_directory` netstring-encodes sorted child names and caps, hashes the result, and performs the same age-based check decision. Mutation methods update `caps`, `local_files`, `last_upload`, and `directories`.

## State, Persistence, And Integration
Persists `private/backupdb.sqlite` tables: `version`, `local_files`, `caps`, `last_upload`, and `directories`. It integrates with `allmydata.util.dbutil.get_db`, Tahoe base32/hash utilities, and `tahoe_backup.BackerUpper`.

## Risks And Test Signals
The cache trusts filesystem timestamps by default, so clock granularity or copied files can cause stale reuse unless `--ignore-timestamps` is used. Randomized health checks make behavior time/probability dependent. Directory hashes depend on deterministic child ordering and byte encodings. Test signals include `allmydata/test/cli/test_backupdb.py` and backup tests that verify reuse, schema upgrades, and timestamp-ignore behavior.
