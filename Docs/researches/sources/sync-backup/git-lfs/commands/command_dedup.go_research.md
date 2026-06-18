<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_dedup.go -->
# sources/sync-backup/git-lfs/commands/command_dedup.go

Purpose: implements `git lfs dedup`, replacing working-tree media files with filesystem-level clones of matching LFS object files when the platform supports clonefile/reflink-like deduplication.

Important APIs/types/functions: `dedupCommand`, `dedupTestCommand`, `dedup`, `dedupFlags.test`, `dedupStats`, `tools.CheckCloneFileSupported`, `tools.CloneFileByPath`, `git.IsWorkingCopyDirty`, and `lfs.NewGitScanner`.

Control flow: `--test` validates platform support and absence of configured LFS extensions. Normal operation verifies repository support, rejects extensions and dirty working trees, scans `HEAD` for LFS pointers, and for each pointer checks local object existence, stats the working-tree file, clone-copies the media object over it, restores mode bits, and updates aggregate stats.

State and persistence behavior: overwrites working-tree files with deduplicated clones from `.git/lfs/objects`, preserving original permissions. It does not change Git history or object storage and depends on a clean worktree to avoid data loss.

Dependencies/integration points: integrates filesystem clone capability detection, LFS object cache paths, Git scanner tree traversal, and command output localization.

Risks and test signals: risks include platform-specific clone semantics, object existence assumptions tied to prior `git status`, extensions being incompatible with raw object deduplication, and only restoring chmod metadata. Test signals include `--test`, unsupported filesystem failure, dirty worktree rejection, successful reflink/clone replacement, missing object skip, and permission preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_dedup.go -->
