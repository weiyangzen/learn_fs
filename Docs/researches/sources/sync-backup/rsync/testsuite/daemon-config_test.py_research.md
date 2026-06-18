# sources/sync-backup/rsync/testsuite/daemon-config_test.py

Purpose: daemon config parser coverage for the `&include` directive and failure behavior for a module whose path does not exist.

Important APIs/types/functions: hand-written `rsyncd.conf`, included config file, `start_test_daemon`, `rsync_argv`, and `test_fail`.

Control flow: build source, write `included.conf` defining `inc-mod`, write main config with `&include included.conf` and a `badpath` module. Start daemon, prove `inc-mod` is reachable and appears in listing, then prove `badpath` refuses a connection.

State and persistence behavior: config files under scratch drive daemon module state. No final data copy is required.

Dependencies and integration points: params.c include parsing, daemon module listing, clientserver path failure.

Risks and test signals: failures show include directive regression or missing-path modules serving unexpectedly.
