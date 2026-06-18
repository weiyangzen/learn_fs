# sources/test-tools/syzkaller/executor/executor_runner.h

Purpose: Long-lived manager-facing runner that multiplexes many child `syz-executor exec` subprocesses, performs host handshake, forwards requests, restarts unhealthy children, and returns flatbuffer results.

Important APIs and control flow: `ProcIDPool` allocates and recycles unique proc IDs. `Proc` owns one child process, request/response shared memory, pipes, current request, output buffer, and state machine (`Started`, `Handshaking`, `Idle`, `Executing`). `Proc::Execute` chooses restart conditions, sends `handshake_req` or `execute_req`, copies program data to shared memory, and reports `ExecutingMessage`. `Ready`, `ReadOutput`, `ReadResponse`, `Restart`, and `HandleCompletion` manage timeouts, stdout capture, failed/hanged requests, proc-id replacement, and `finish_output`. `Runner` receives manager messages, tracks request queue, builds feature info, handles signal updates/state requests/corpus triaged notifications, and runs optional leak checks. `runner` installs signal handlers, connects to the manager, pads fd numbers, and starts `Runner`.

State and dependencies: runner state persists across requests: proc freshness, queued requests, coverage filters, feature setup results, leak frames, and corpus triage status. Depends on `Connection`, `Subprocess`, `ShmemFile`, `CoverFilter`, flatrpc, and OS feature functions.

Integration points: selected by `main argv[1] == "runner"`; manager protocol implementation must match Go RPC server cookie hashing and message schemas.

Risks and tests: restart/hang behavior is subtle because killed top processes may leave descendant test processes alive. Shared-memory bounds rely on `kMaxInput`/`kMaxOutput` matching executor constants. Repeated failures escalate to `SYZFAIL`. Test signals are integration-heavy; `StateRequest` offers live diagnostic output.
