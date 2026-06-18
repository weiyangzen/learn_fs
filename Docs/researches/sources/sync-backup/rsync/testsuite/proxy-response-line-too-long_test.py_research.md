## sources/sync-backup/rsync/testsuite/proxy-response-line-too-long_test.py

Purpose: regression test for an off-by-one stack out-of-bounds write in HTTP proxy response parsing.

Important APIs and control flow: requires real TCP via `require_tcp()`, claims fixed port 12873, starts an in-process loopback listener that accepts one CONNECT-style client, reads request headers, sends exactly 1023 `X` bytes without a newline, and closes. It runs rsync against an irrelevant daemon URL with `RSYNC_PROXY` pointing to the fake proxy, then checks the process did not die by signal, did not return success, and emitted `proxy response line too long`.

State and dependencies: binds a TCP socket, uses `claim_ports`, a serving thread, environment variable `RSYNC_PROXY`, and `SCRATCHDIR/workdir`.

Integration points: tests `establish_proxy_connection()` error handling and process safety.

Risks and test signals: only runs in `--use-tcp` mode. Strong signals are non-signal nonzero exit and exact stderr diagnostic.
