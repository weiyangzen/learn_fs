# sources/sync-backup/borg/docs/usage/compact.rst.inc

Purpose: generated reference for `borg compact`, which frees repository space by deleting unreferenced objects.

Important APIs and control flow: options are `--dry-run` and `--stats`. The command analyzes all existing archives, determines referenced repository objects, and deletes unused objects. With `--stats`, it lists all objects to compute stored sizes and builds/caches a fresh chunks index.

State and persistence: mutates repository object storage by deleting unreferenced chunks. It also affects recoverability: soft-deleted archives can no longer be undeleted afterward.

Dependencies and integration points: follows `delete`/`prune`, interrupted create cleanup, repository corruption/lost archive detection, chunks index caching, and `check --find-lost-archives`.

Risks: compact can permanently remove data for soft-deleted or lost archives. Running immediately after interrupted backups can discard data that a retry might reuse. `--stats` may be much slower for some repositories.

Test signals: dry-run non-mutation, unused object deletion, stats before/after accounting, undelete failure after compact, and behavior with lost archive fixtures.
