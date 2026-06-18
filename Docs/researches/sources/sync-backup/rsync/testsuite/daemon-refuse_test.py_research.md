# sources/sync-backup/rsync/testsuite/daemon-refuse_test.py

Purpose: broader daemon `refuse options` coverage for named options, wildcard patterns, and allow-list negation syntax.

Important APIs/types/functions: `write_daemon_conf`, `refused`, `allowed`, `verify_dirs`, `start_test_daemon`, `rsync_argv`, and `make_tree`.

Control flow: configure modules refusing `delete`, refusing `checksum*`, and allowing only `-a`/`-v` via `* !a !v`. Assert `--delete` push is refused but plain push succeeds, `--checksum` pull is refused by wildcard, `-av` pull is allowed, and `-avz` is refused by allow-list module.

State and persistence behavior: allowed cases verify actual destination data, not just exit code.

Dependencies and integration points: daemon option parser/refusal engine, wildcard option matching, negated allow-list semantics, and transfer verification.

Risks and test signals: failures indicate option names are not normalized/matched correctly or allowed transfers are falsely blocked.
