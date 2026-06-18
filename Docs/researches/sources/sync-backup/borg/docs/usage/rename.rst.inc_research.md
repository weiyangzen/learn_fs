# sources/sync-backup/borg/docs/usage/rename.rst.inc

Purpose: Documents `borg rename`, which renames an archive within a repository.

Important APIs/types/functions: CLI contract is `borg [common options] rename [options] OLDNAME NEWNAME`. There are no command-specific options.

Control flow: Runtime resolves `OLDNAME`, validates `NEWNAME`, writes new archive metadata/name, and produces a different archive ID as documented.

State and persistence: Mutates archive metadata and repository manifest/archive index state. The content payload is conceptually unchanged, but archive identity changes.

Dependencies and integration points: Integrates with archive name resolution, manifest persistence, `repo-list`, and commands that match archives by name or ID.

Risks: Automation that tracks archive IDs must account for ID changes after rename. Name collision handling must be correct to avoid overwriting or hiding archives.

Test signals: Functional tests should cover successful rename, nonexistent source, duplicate destination, ID change, preserved contents, and listing by old/new names.
