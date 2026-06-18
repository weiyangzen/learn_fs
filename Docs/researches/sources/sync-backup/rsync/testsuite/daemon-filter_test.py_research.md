# sources/sync-backup/rsync/testsuite/daemon-filter_test.py

Purpose: daemon-side filter and chmod coverage: `exclude`, `incoming chmod`, and `outgoing chmod` at depth.

Important APIs/types/functions: `write_daemon_conf`, `pull`, `assert_not_exists`, `assert_same`, `assert_mode`, `walk_files`, `rsync_argv`, and `test_fail`.

Control flow: build depth-3 tree and secret files, configure modules for exclude, incoming chmod `F600`, and outgoing chmod `Fg-r,Fo-r`. Pull filtered module and verify secrets absent but normal files present. Push into incoming module and check every file mode is 0600. Pull outgoing module and ensure group/other read bits are cleared on every file.

State and persistence behavior: destination backing directories show daemon-side mode rewriting and filter application.

Dependencies and integration points: daemon filter rules, incoming/outgoing chmod parameters, file mode preservation, and harness assertions.

Risks and test signals: loops check non-vacuous file counts. Failures indicate filters not applied at depth or chmod rewrite gaps.
