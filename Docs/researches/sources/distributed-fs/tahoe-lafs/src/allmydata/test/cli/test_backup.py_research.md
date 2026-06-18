# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_backup.py

## Purpose
Exercises the `tahoe backup` CLI end to end and at option-parsing boundaries. It verifies backup creation, archive/latest layout, backupdb reuse, progress reporting, exclude filters, Unicode patterns, tilde expansion, and graceful handling of unsupported or unreadable filesystem entries.

## Important APIs, Types, And Functions
`Backup` mixes `GridTestMixin`, `CLITestMixin`, and `StallMixin`. Helpers `writeto()`, `count_output()`, `count_output2()`, and `progress_output()` create local files and parse CLI summaries. `_check_filtering()` validates filter results. `_ignore_something_test()` is shared by symlink and FIFO skip tests. Individual tests cover full backup lifecycle, exclude options, Unicode excludes, `--exclude-from-utf-8` tilde expansion, ignored symlinks/FIFOs, unreadable files/directories, and alias error paths.

## Control Flow
The full backup test creates a local tree, creates a Tahoe alias, runs verbose backup, inspects `Latest` and `Archives`, reads restored file content, repeats backups to verify reuse and health checks, forces backupdb timestamps stale, modifies local file/directory types, and verifies new archive immutability. Option tests parse command options without a live grid and call `filter_listdir()`.

## State And Persistence
Tests create local source trees, node directories, Tahoe grid state, backup archives, and `backupdb.sqlite`. Some tests patch `open()` or chmod files/directories, with cleanup restoring permissions.

## Dependencies And Integration Points
Depends on backup CLI, backupdb, file utilities, encoding utilities, namespace helper, Twisted monkey patching, no-network grid, and CLI common helpers.

## Risks And Test Signals
Risks include backupdb false reuse, archive mutation, progress regressions, platform-specific filesystem behavior, Unicode glob handling, and poor user errors for missing aliases. Signals include exact uploaded/reused/skipped counts, monotonic progress tuples, `Latest` and `Archives` contents, old archive content staying unchanged, expected exclusion sets, warnings and return code 2 for skipped symlinks/FIFOs/unreadable paths, and return code 1 with `error:` for alias failures.
