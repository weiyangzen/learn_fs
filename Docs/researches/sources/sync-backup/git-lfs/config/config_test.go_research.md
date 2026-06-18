<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config_test.go -->
# sources/sync-backup/git-lfs/config/config_test.go

## Research

This file exercises the main `Configuration` behavior using `NewFrom` maps rather than real Git config files. It covers default remote fallback, branch remote precedence, push-remote precedence, `remote.lfsdefault` and `remote.lfspushdefault`, basic/tus transfer booleans including invalid values, extension parsing, fetch include/exclude cleanup, repository permissions from `core.sharedrepository`, committer/author identity precedence, timestamp parsing, and remote names containing dots.

The tests are pure unit tests with no persistent state beyond process maps and the captured `timestamp` field. They provide strong signals for precedence and conversion rules but do not cover real Git command failures, delayed config source loading, filesystem initialization, hook path expansion, config writes, concurrency, or `.lfsconfig` unsafe key warnings. They also intentionally rely on current process `umask()` for expected permission defaults.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config_test.go -->
