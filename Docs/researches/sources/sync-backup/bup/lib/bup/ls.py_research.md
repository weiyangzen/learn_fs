<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/ls.py -->
# sources/sync-backup/bup/lib/bup/ls.py

## Purpose
This module implements shared logic for `bup ls`: resolving repository VFS paths and formatting listings in short, hash, classified, or long metadata-rich forms.

## Important APIs, Types, And Functions
Key pieces are `item_hash()`, `item_info()`, the `optspec`, `LsOpts`, `opts_from_cmdline()`, `within_repo()`, and `via_cmdline()`.

## Control Flow
`opts_from_cmdline()` parses command arguments and maps raw flags into semantic options such as classification and hidden-file mode. `via_cmdline()` opens the selected local/remote repo and calls `within_repo()`. `within_repo()` resolves each requested path via `vfs.resolve()` or `vfs.try_resolve()`, optionally lists directory contents, augments metadata when needed, filters hidden entries, formats lines, and columnates tty short output.

## State And Persistence Behavior
The module has no persistent state. It reads repository objects and metadata through the repo/VFS layers and writes formatted bytes to the provided output stream.

## Dependencies And Integration Points
It depends on `metadata.summary_bytes`, `vfs`, `xstat.classification_str`, `Options`, terminal helpers, and `repo.main_repo_location`/`repo_for_location`. It is a command-facing consumer of repo/local and repo/remote abstractions.

## Risks And Edge Cases
Long listings require metadata augmentation, which can trigger object reads and public metadata filtering. Hidden-file behavior must match common `ls -a`/`-A` expectations, including synthetic `..`. `commit_hash` implies hash display and changes what hash is printed for commit items. Errors from VFS resolution are logged and reflected in a nonzero return.

## Test Signals
`test/ext/test-ls`, `test/ext/test-ls-remote`, VFS integration tests, and metadata listing tests cover path resolution, hidden entries, classification suffixes, hash display, remote behavior, and long-format output.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/ls.py -->
