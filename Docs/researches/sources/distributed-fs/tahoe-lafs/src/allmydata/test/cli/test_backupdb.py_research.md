# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_backupdb.py

## Purpose
Tests the SQLite backup database used by `tahoe backup` to avoid unnecessary uploads and directory creation. It covers database creation, schema upgrade, failure modes, file result caching, directory result caching, timestamp-based rechecks, type changes, and Unicode filenames.

## Important APIs, Types, And Functions
`BackupDB.create()` wraps `backupdb.get_backupdb()`. `writeto()` creates test files. Tests exercise `BackupDB.VERSION`, v1-to-v2 upgrade, unusable database errors, wrong-version handling, `check_file()`, `FileResult.did_upload()`, `was_uploaded()`, `should_check()`, `check_directory()`, `DirectoryResult.did_create()`, `was_created()`, and `did_check_healthy()`.

## Control Flow
Tests create a db file, record upload results for files or directories, reopen/check records, modify file contents and timestamps, force freshness thresholds with `NO_CHECK_BEFORE` and `ALWAYS_CHECK_AFTER`, and assert cache hit/miss behavior. Failure tests put a text file or directory where SQLite expects a database and assert diagnostic stderr.

## State And Persistence
The database persists version rows, file upload records, directory content hashes/caps, and last-check timestamps under test directories. The tests also persist local files with byte and Unicode names and mutate filesystem types.

## Dependencies And Integration Points
Depends on `allmydata.scripts.backupdb`, file utilities, Unicode listdir helpers, Trial, `StringIO`, and platform filename representability checks.

## Risks And Test Signals
Risks include unsafe schema upgrades, stale cache hits after content/type changes, string/bytes cap type drift, unreliable timestamp freshness, and Unicode path mishandling. Signals include version 2 after creation/upgrade, `None` plus clear stderr for unusable dbs, old-version rejection text, bytes returned from cached caps, `should_check()` threshold changes, directory cache misses on changed children, and skipped Unicode tests when filenames cannot be represented.
