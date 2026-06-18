# sources/test-tools/syzkaller/executor/conn.h

Purpose: RPC and readiness primitives for the executor runner process.

Important APIs and control flow: `Connection` connects to a manager address/port or uses `stdin`, sends and receives size-prefixed flatbuffers, and retries partial `read`/`write` operations across `EINTR`/`EAGAIN`. `Connect` handles localhost IPv4/IPv6 fallback, numeric addresses, DNS via `gethostbyname`, and blocking connect interruption through `ConnectWait`. `Select` wraps `pselect`: `Arm` adds fds, `Wait` blocks with millisecond timeout, `Ready` tests readiness, and `Prepare` sets nonblocking mode.

State and dependencies: `Connection` owns an fd, a receive buffer, and a reusable `FlatBufferBuilder`. It assumes little-endian size prefixes via `le32toh`. `Select` owns a single fd set and max fd and is intended per-loop, not reusable after `Wait` without rearming.

Integration points: `executor_runner.h` uses `Connection` for host-manager messages and `Select` for multiplexing the manager socket plus subprocess response/stdout pipes.

Risks and tests: `Connection::Recv` trusts the remote size prefix and resizes memory accordingly, so manager/executor protocol trust is required. `stdin` mode returns fd 0 while `Send` writes back to the same fd, so it relies on an external bidirectional setup. Test signals are indirect through runner integration; this file is exempted from some fuzzer-only style checks in `style_test.go`.
