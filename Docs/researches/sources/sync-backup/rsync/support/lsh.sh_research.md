<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh.sh -->
# sources/sync-backup/rsync/support/lsh.sh

Purpose: simpler POSIX-shell local remote-shell shim for rsync tests that only pretends to connect to `localhost` or `lh`.

Important APIs/types/functions: no functions; it parses a small subset of ssh-like options, `-l USER`, and `--no-cd`.

Control flow: consume options until host, reject non-local hosts, set `do_cd=n` for `lh`, optionally build a `sudo -H -u USER sh -c` command with a home-directory `cd`, otherwise chdir to the current user's home when requested and `eval` the remaining command.

State and persistence behavior: may change current directory and may execute through sudo. No persistent files are touched.

Dependencies and integration points: depends on `/bin/sh`, `sed`, `perl` for home lookup under `-l`, and sudo for alternate users. It is used by tests such as `testsuite/00-hello_test.py` through `RSYNC_RSH`.

Risks: `eval "${@}"` deliberately applies shell parsing to the remote command and should remain test-only. It ignores many options without validating their arguments beyond the simple parser. Host validation is intentionally narrow.

Test signals: rsync local remote-shell transfers to and from `lh:` and `localhost:`, `-l USER` paths, and arguments containing shell-special characters.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh.sh -->
