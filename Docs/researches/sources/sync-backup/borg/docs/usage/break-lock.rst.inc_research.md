# sources/sync-backup/borg/docs/usage/break-lock.rst.inc

Purpose: generated reference for `borg break-lock`, an emergency command for removing repository and cache locks.

Important APIs and control flow: no command-specific options beyond common options. The runtime path must reach both repository lock and cache lock handling and forcibly clear stale lock records.

State and persistence: mutates lock state in the repository and local cache. It does not inspect or change archive contents.

Dependencies and integration points: coupled to Borg's locking implementation, host identity/stale-lock behavior, cache directory, repository location, and lock wait semantics.

Risks: using it while any Borg process on any machine still accesses the repository or cache can corrupt state or break active operations. Documentation intentionally keeps the command terse and cautionary.

Test signals: unit/integration tests should cover stale lock removal while ensuring normal active lock acquisition still protects live processes.
