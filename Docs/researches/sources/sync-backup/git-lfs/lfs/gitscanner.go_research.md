# sources/sync-backup/git-lfs/lfs/gitscanner.go

Purpose: public dispatcher for scanning Git history, refs, trees, index, stashes, and previous versions for LFS pointers.

Important APIs/types/functions: `GitScanner`, `GitScannerFoundPointer`, `GitScannerFoundLockable`, `GitScannerSet`, `NewGitScanner`, `NewGitScannerForPush`, all `Scan*` methods, and `firstGitScannerCallback`.

Control flow: each method resolves a callback, sets mode flags such as range-to-remote, skip-deleted, or commits-only, then delegates to specialized helpers (`scanRefsToChan`, `scanRefsByTree`, `runScanTree`, `scanUnpushed`, `logPreviousSHAs`, `scanIndex`). Performance timings are traced.

State/persistence behavior: scanner methods mutate the receiver's mode flags, remote/skipped refs, and callback fields. Scanning itself is read-only except for underlying Git commands that may refresh indexes in some paths.

Dependencies/integration: central integration point for `git/rev-list`, `git cat-file`, `git ls-tree`, log parsing, filepath filters, push lockable checks, and config environments.

Risks/test signals: receiver is stateful and not safe to reuse concurrently across scan types without resetting flags. Missing callbacks return a sentinel error. Tests in this group cover pointer scanner pieces; broader scanner behavior is covered in other files not in this work item.
