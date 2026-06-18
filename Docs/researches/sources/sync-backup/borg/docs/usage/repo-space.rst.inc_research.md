# sources/sync-backup/borg/docs/usage/repo-space.rst.inc

Purpose: Documents `borg repo-space`, which manages reserved emergency space inside a repository.

Important APIs/types/functions: CLI contract is `borg [common options] repo-space [options]`. Options are `--reserve SPACE` and `--free`.

Control flow: Runtime checks current reservation when no mutating option is supplied, writes reservation objects rounded to 64 MiB blocks for `--reserve`, or removes all reservation objects for `--free`.

State and persistence: Mutates repository storage by adding/removing reserved-space objects. The reserved space is intentionally expendable to recover from disk-full conditions.

Dependencies and integration points: Integrates with repository locking and space management, plus prune/delete/compact emergency recovery workflows.

Risks: If users free reserved space and forget to reserve it again, future disk-full events can become unrecoverable because Borg cannot lock or compact. Reservation size rounding must be clear.

Test signals: Cover reserve/free/idempotency, block rounding, reporting, behavior on nearly full filesystems, and interaction with compact after emergency cleanup.
