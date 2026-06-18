<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_smudge.go -->
# sources/sync-backup/git-lfs/commands/command_smudge.go

Purpose: implements the Git smudge filter and delayed smudge helper, converting LFS pointers into media content or leaving pointers when skipped/filtered.

Important APIs/types/functions: global `smudgeSkip`; `delayedSmudge`, `smudge`, `smudgeCommand`, `smudgeFilename`, and `possiblyMalformedObjectSize`; `lfs.DecodeFrom`, `GitFilter.Smudge`, `tools.Spool`, `tq.TransferQueue`, and filepath filters.

Control flow: `smudgeCommand` requires stdin, sets up repo/hooks, honors `GIT_LFS_SKIP_SMUDGE`, builds filter, and calls `smudge`. `smudge` decodes pointer input or spools non-pointers back out, links/copies reference objects, creates a progress callback, writes pointer unchanged if skipped/excluded, otherwise downloads/smudges object and falls back to writing pointer plus logging on errors. `delayedSmudge` supports filter-process delay by queueing missing allowed objects and returning status delay, or writing content/pointer immediately.

State and persistence behavior: downloads media into local object storage, writes media or pointer bytes to stdout/pktline writer, creates temp spool files for non-pointer passthrough, and may log download errors.

Dependencies/integration points: used directly by Git smudge filter and by filter-process. Integrates transfer manifest downloads, include/exclude config, reference storage, skip-download-errors behavior, and Windows large-file warnings.

Risks and test signals: risks include writing pointer fallback after partial smudge errors, callback file close only after smudge path, delayed queue requiring caller-managed status writes, and 4 GiB Windows warning heuristic. Test signals include valid pointer download, local object smudge, skip smudge, excluded path, non-pointer passthrough, missing object with skipDownloadErrors true/false, delayed missing object, delayed present object, and large object warning.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_smudge.go -->
