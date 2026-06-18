<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fsck.go -->
# sources/sync-backup/git-lfs/commands/command_fsck.go

Purpose: implements `git lfs fsck`, validating local LFS object contents and pointer canonicality for selected refs/ranges/index state, and quarantining corrupt media objects unless dry-run is set.

Important APIs/types/functions: globals `fsckDryRun`, `fsckObjects`, `fsckPointers`; `corruptPointer`; `fsckCommand`, `doFsckObjects`, `doFsckPointers`, and `fsckPointer`. It uses `lfs.GitScanner`, `filepathfilter`, `sha256`, `cfg.Filesystem().ObjectPathname`, and pointer scan errors.

Control flow: installs hooks, resolves current ref or a single ref/range argument, defaults to both object and pointer checks, scans pointer references for media objects and hashes local files, scans by tree for noncanonical or unexpected Git objects, prints OK or errors, and moves corrupt object files into `.git/lfs/bad` unless dry-run or only pointer corruption occurred.

State and persistence behavior: read-mostly validation, but non-dry corrupt object repair creates the bad directory and renames corrupt media files into it. Zero-size missing objects are accepted.

Dependencies/integration points: integrates ref resolution, index scanning, fetch-exclude filters to avoid expected missing subsets, LFS object storage layout, and pointer scanner canonicality metadata.

Risks and test signals: risks include limited argument parsing, only one ref/range supported, hashing large files without progress, dry-run exit semantics, and object quarantine rename failures. Test signals include valid repo OK, corrupt media hash detection, missing nonzero object, zero-size pointer, noncanonical pointer, unexpected Git object, index scanning with no args, and dry-run no quarantine.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_fsck.go -->
