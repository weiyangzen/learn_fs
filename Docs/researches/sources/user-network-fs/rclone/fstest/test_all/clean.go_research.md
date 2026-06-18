
# sources/user-network-fs/rclone/fstest/test_all/clean.go

Purpose: cleanup support for `test_all -clean`, removing leftover randomized integration-test directories from configured remotes.

Important APIs/types/functions: `MatchTestRemote` identifies names like `rclone-test-<random>` plus optional `_segments`. `cleanFs` optionally runs backend cleanup, lists top-level directories, and purges matching test dirs. `cleanRemotes` iterates configured backends.

Control flow: `cleanFs` opens the remote, optionally calls `operations.CleanUp`, lists sorted directories, joins remote root and directory path, and purges each matching directory unless dry-run is set. Errors are logged and the last cleanup/purge error is returned.

State/persistence: mutates external remotes by deleting test directories. It does not edit local files except through logging.

Dependencies/integration: uses rclone `fs`, `fspath`, `list`, `operations`, and `runs.Config`. The regex is copied from fstest naming to avoid importing extra flags.

Risks: cleanup is intentionally destructive for names matching the test pattern. If a user has real data matching that pattern in a configured remote root, it can be purged. Listing failures abort the remote cleanup.

Test signals: no direct tests here; dry-run logging and integration cleanup outcomes are the main operational signals.
