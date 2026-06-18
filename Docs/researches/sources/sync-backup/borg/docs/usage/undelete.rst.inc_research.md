# sources/sync-backup/borg/docs/usage/undelete.rst.inc

Purpose: Documents `borg undelete`, which restores soft-deleted archives before compaction permanently frees their data.

Important APIs/types/functions: CLI contract is `borg [common options] undelete [options] [NAME]`. Options include `--dry-run`, `--list`, and archive filters.

Control flow: Runtime selects soft-deleted archives by name or filters, previews them under dry-run/list, and moves archive metadata/data back to live state when executed.

State and persistence: Mutates repository archive deletion state. It only works before `borg compact`; after compaction, data occupied only by soft-deleted archives is gone.

Dependencies and integration points: Integrates with prune/delete soft-deletion, `repo-list --deleted`, archive matching, and compact.

Risks: Users may assume undelete works after compaction; the document warns it does not. Broad archive filters can undelete more archives than intended.

Test signals: Cover undelete by name, match filters, dry-run/list output, after-prune restoration, behavior after compact, and multiple deleted archives with time/name filters.
