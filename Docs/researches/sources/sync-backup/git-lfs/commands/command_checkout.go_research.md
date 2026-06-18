<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_checkout.go -->
# sources/sync-backup/git-lfs/commands/command_checkout.go

Purpose: implements `git lfs checkout`, replacing LFS pointer files in the working tree with locally cached media files, and supports extracting a specific conflict stage to a chosen path.

Important APIs/types/functions: globals `checkoutTo`, `checkoutBase`, `checkoutOurs`, `checkoutTheirs`; `checkoutCommand`, `checkoutConflict`, `whichCheckout`, and `rootedPathPatterns`. It uses `setupRepository`, `git.CurrentRef`, `git.ResolveRef` stage syntax, `lfs.NewGitScanner`, `newSingleCheckout`, `filepathfilter.New`, `lfs.NewCurrentToRepoPatternConverter`, `lfs.NewCurrentToRepoPathConverter`, `tasklog`, and `tq.Meter`.

Control flow: the command validates repository/worktree state, parses mutually exclusive conflict stage flags, then either performs conflict checkout via `checkoutConflict` or scans LFS files at the current ref filtered by rooted path patterns. It records pointer sizes in a checkout meter, then runs single checkout for each pointer. Conflict checkout converts paths to repository-relative names, resolves `:<stage>:<file>`, decodes the pointer object, and writes the matching media to `--to`.

State and persistence behavior: normal checkout mutates working-tree files by linking/copying from `.git/lfs/objects`; conflict checkout creates parent directories for the `--to` path and writes a standalone output file. No remote download is attempted, so missing local media remains a checkout failure or skip through `singleCheckout`.

Dependencies/integration points: depends on index stage semantics, Git object scanning, LFS pointer decoding, tasklog progress, path conversion from current directory to repository root, and the `singleCheckout` implementation outside this subset.

Risks and test signals: risks include silent return rather than nonzero exit for bare repositories, only local-cache availability, path conversion edge cases from subdirectories, and meter byte accounting being serial rather than callback-driven. Test signals include checking out all pointers, filtered paths, bare repository behavior, missing object behavior, and conflict-stage extraction for base/ours/theirs with exactly one path.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_checkout.go -->
