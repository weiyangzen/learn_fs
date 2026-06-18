# sources/sync-backup/borg/docs/usage/check.rst.inc

Purpose: generated reference for `borg check`, the repository and archive consistency verifier.

Important APIs and control flow: command options select repository-only checks, archive-only checks, cryptographic data verification, repair, lost-archive search, and bounded partial checks with `--max-duration`. Repository checks validate object headers, metadata, data size, and hashes; archive checks validate manifest, archive metadata chunks, item references, and optionally file data.

State and persistence: read-only by default. Partial repository checks persist progress. `--repair` can remove corrupted objects, remove or restore archive directory entries, and replace missing file chunks with damage markers/zero runs.

Dependencies and integration points: archive filtering, remote execution split (repository checks on server, archive checks on client), encryption keys for archive checks, compact/undelete semantics, and return-code/logging behavior.

Risks: `--repair` is explicitly lossy and dangerous. `--max-duration` excludes archive checks and repair. `--find-lost-archives` is very expensive and only useful before compact removes data.

Test signals: parser conflict tests, repository corruption fixtures, missing chunk/archive metadata fixtures, partial-check resume/abort behavior, remote repo checks, and repair-mode confirmation handling.
