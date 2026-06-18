<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_commit.go -->
# sources/sync-backup/git-lfs/commands/command_post_commit.go

Purpose: implements the `post-commit` hook command that fixes read-only flags for lockable files changed in the new commit.

Important APIs/types/functions: `postCommitCommand`, `newLockClient`, `git.GetFilesChanged`, `FixLockableFileWriteFlags`, and `cfg.SetLockableFilesReadOnly`.

Control flow: returns when read-only lockable support is disabled, validates Git version, creates a lock client, skips when there are no lockable patterns, diffs `HEAD` against the working tree baseline via `git.GetFilesChanged("HEAD", "")`, and fixes write flags for those files.

State and persistence behavior: mutates working-tree file permissions after commit, mainly for newly added lockable files that might otherwise remain writable.

Dependencies/integration points: installed as a Git hook, integrates lockable attribute patterns, lock cache/client behavior, and Git changed-file detection.

Risks and test signals: risks include exiting with code 1 on changed-file diff errors, but only logging permission-fix errors; changed-file semantics around root commits may matter. Test signals include disabled setting, no patterns, added lockable files becoming read-only, locked files remaining writable, and diff failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_commit.go -->
