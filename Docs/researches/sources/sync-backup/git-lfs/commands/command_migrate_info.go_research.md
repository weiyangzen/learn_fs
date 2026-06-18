<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_info.go -->
# sources/sync-backup/git-lfs/commands/command_migrate_info.go

Purpose: implements `git lfs migrate info`, scanning selected history and summarizing large file usage by extension or file name, with optional LFS pointer treatment modes and fixup inference.

Important APIs/types/functions: `migrateInfoPointersType`, globals `migrateInfoTopN`, `migrateInfoAboveFmt`, `migrateInfoUnitFmt`, `migrateInfoPointers`, `migrateInfoPointersMode`; `migrateInfoCommand`, `MigrateInfoEntry`, `findEntryByExtension`, `MapToEntries`, `removeEmptyEntries`, `EntriesBySize`, and `EntriesBySize.Print`.

Control flow: opens DB and history rewriter, parses byte threshold and optional unit, parses `--pointers` mode, validates `--fixup`, then uses migrate's rewrite walk with blob callbacks that optionally follow/ignore/no-follow LFS pointers, group entries by extension or basename, and count total/above-threshold bytes. Root tree pre-callback validates `.gitattributes` or loads fixup attributes. Results are sorted descending by size, truncated to `--top`, optionally append a separate LFS Objects row, and printed tabularly.

State and persistence behavior: read-only history traversal; counters are in memory. It still uses migrate's ref selection and remote fetch behavior, but no refs are updated because callbacks return original blobs/trees.

Dependencies/integration points: depends on `githistory.Rewriter` as a scanner, LFS pointer decoding, Git attributes fixup tree, humanize byte parsing/formatting, and shared migrate flags.

Risks and test signals: risks include using rewrite machinery for reporting, pointer mode defaults depending on global initialization, percentage formatting when totals are nonzero only, symlink `.gitattributes` rejection, and top truncation before adding LFS pointer summary. Test signals include thresholds, unit formatting, pointer follow/no-follow/ignore, fixup with attributes, include/exclude incompatibility, sort tie order, no matching files, and top count clamping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_info.go -->
