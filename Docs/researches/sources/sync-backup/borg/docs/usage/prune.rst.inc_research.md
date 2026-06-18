# sources/sync-backup/borg/docs/usage/prune.rst.inc

Purpose: Documents `borg prune`, which soft-deletes archives not retained by specified retention rules.

Important APIs/types/functions: CLI contract is `borg [common options] prune [options] [NAME]`. Key options are `--dry-run`, list controls, `--format`, `--keep-within`, `--keep-last/--keep-secondly`, minutely/hourly/daily/weekly/monthly/quarterly/yearly retention counts, and archive filters.

Control flow: Runtime identifies candidate archives by `NAME` or archive filters, applies `--keep-within` first, then retention buckets from secondly through yearly, marks non-kept archives as soft-deleted, and optionally lists kept/pruned items. It does not free disk space by itself.

State and persistence: Mutates archive deletion state in the repository. Actual object space persists until `borg compact`; `borg undelete` can reverse soft deletion before compaction.

Dependencies and integration points: Integrates with archive matching, `repo-list --deleted`, `undelete`, `compact`, and automated backup rotation scripts. Time calculations use the local timezone where prune runs and weeks run Monday to Sunday.

Risks: If no `NAME` or `--match-archives` is supplied, all archives are candidates, which is dangerous for shared repositories. Negative keep counts mean unlimited retention. Users may expect disk space to be freed immediately, but compaction is required.

Test signals: Tests should cover retention bucket ordering, `--keep-within`, oldest archive retention fallback, multiple archive series filtering, dry-run/list output, deleted state, and post-prune compaction/undelete interactions.
