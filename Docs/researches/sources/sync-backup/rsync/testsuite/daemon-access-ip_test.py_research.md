# sources/sync-backup/rsync/testsuite/daemon-access-ip_test.py

Purpose: real-TCP daemon coverage for numeric `hosts allow`/`hosts deny` exact-IP and CIDR matching, plus client `--address`.

Important APIs/types/functions: `require_tcp`, hand-written config, `start_test_daemon`, `connect(mod)`, `rsync_argv`, and `test_fail`.

Control flow: require TCP because stdio daemon has no peer IP. Build source tree and daemon modules with exact allow, CIDR allow, CIDR deny, and nonmatching allow rules. Start daemon, assert allowed modules connect and denied modules fail, then assert `--address=127.0.0.1` can bind and connect to the CIDR-allowed module.

State and persistence behavior: no data copy is required; connection success/refusal is the state under test.

Dependencies and integration points: rsync daemon access.c address matching, real loopback socket transport, and socket local bind.

Risks and test signals: global allow settings are intentionally omitted to avoid short-circuiting module rules. Failure means IP/CIDR ACL decisions or client bind behavior regressed.
