# sources/distributed-fs/tahoe-lafs/src/allmydata/util/dbutil.py

## Purpose

This module centralizes SQLite database open/create/version-upgrade behavior. It is used by Tahoe components such as backup database code that need a schema version table and migration scripts.

## APIs and control flow

`DBError` wraps open, compatibility, and version failures. `get_db()` opens or creates a SQLite file, enables foreign keys, executes the initial schema and inserts the target version for new databases, reads the `version` table, applies sequential updater scripts while `version < target_version`, and verifies the final version. `just_create` returns immediately after creation/version read for tests.

## State, dependencies, risks, and tests

Persistent state is the SQLite file and its `version` table. Dependencies are `sqlite3`, `os.path.exists`, and optional stderr naming. The parent directory must already exist.

Risks include updater scripts needing to update the `version` table consistently with the loop, failure after partial migration commits, no explicit transaction wrapping across multi-version upgrades, and treating incompatible files as `DBError`. Test signals should cover fresh creation, foreign-key enforcement, unusable files, missing updater paths, sequential migrations, `just_create`, and open failures.
