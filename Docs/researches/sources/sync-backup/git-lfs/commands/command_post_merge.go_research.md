<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_merge.go -->
# sources/sync-backup/git-lfs/commands/command_post_merge.go

Purpose: implements the `post-merge` hook command that reapplies read-only permissions for all lockable files after merges.

Important APIs/types/functions: `postMergeCommand`, `newLockClient`, `FixAllLockableFileWriteFlags`, and `cfg.SetLockableFilesReadOnly`.

Control flow: validates the single Git hook squash flag argument, returns if read-only lockable behavior is disabled, validates Git version, creates a lock client, skips when no lockable patterns exist, then scans all lockable files because the hook does not report changed paths.

State and persistence behavior: mutates working-tree permissions for lockable files. It does not change repository data or refs.

Dependencies/integration points: installed as Git post-merge hook, depends on lockable patterns and lock client permission logic.

Risks and test signals: risks include full-repo scan cost after every merge, warning-only failure behavior, and no use of squash flag. Test signals include invalid arg count, disabled setting, no patterns, merge with lockable files, and permission-fix failures logged.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_merge.go -->
