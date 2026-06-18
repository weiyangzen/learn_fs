# sources/sync-backup/borg/docs/usage/delete.rst.inc

Purpose: generated reference for `borg delete`, which soft-deletes one or more archives.

Important APIs and control flow: accepts optional archive `NAME`, `--dry-run`, `--list`, and archive filters including `--match-archives`, sort, first/last, and age windows. Multiple archives can be selected through match patterns.

State and persistence: marks archives for deletion in the repository but does not free disk space. The data remains recoverable with `borg undelete` until compaction.

Dependencies and integration points: archive matching help, repository manifest/archive directory, undelete, compact, and safety prompts/automatic answerers.

Risks: archive names need not be unique, so deleting by name or broad filters can affect multiple archives. Users may incorrectly expect disk space to be freed before compact.

Test signals: dry-run/list output, duplicate-name behavior, filter combinations, soft-delete visibility in repo-list/undelete, and compact making deletion permanent.
