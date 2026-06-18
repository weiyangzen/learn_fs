<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pull.go -->
# sources/sync-backup/git-lfs/commands/pull.go

## Research

This file implements the checkout side used after LFS objects are fetched. `newSingleCheckout` inspects `filter.lfs.clean`, moves to the working tree root when possible, and returns either `singleCheckout` or `noOpCheckout` for bare/disabled-filter cases. The public surface in this package is the `abstractCheckout` contract: `Manifest`, `Skip`, `Run`, `RunToPath`, and `Close`.

`singleCheckout.Run` validates that the worktree path is safe to write, decodes any existing pointer, avoids overwriting non-pointer content or a pointer for a different OID, creates missing directories, smudges content through `lfs.GitFilter.SmudgeToFile`, then stages the path through `gitIndexer`. State is local process state: a lazily-created transfer manifest and a long-lived `git update-index --stdin` subprocess guarded by a mutex. Dependencies include `config.Environment`, `git`, `lfs`, `tools.DirWalker`, `tq.Manifest`, and command-level error reporting. Risks are race-prone worktree mutations, preserving user edits, deleted-index paths, and correct cleanup of the update-index process. There is no direct test file here; behavior is indirectly signaled by checkout/fetch integration and by `gitIndexer` subprocess failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pull.go -->
