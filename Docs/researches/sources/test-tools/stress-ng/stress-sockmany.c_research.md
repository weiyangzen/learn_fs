# sources/test-tools/stress-ng/stress-sockmany.c

## Purpose

`stress-sockmany.c` implements `sockmany`, a stressor that opens many simultaneous IPv4 TCP connections to a local server. It is aimed at file descriptor limits, ephemeral port exhaustion, TCP accept/connect paths, listen backlog behavior, and small-message send/receive throughput.

## Important APIs, Types, and Functions

- `stress_sock_fds_t` is a shared mmap structure that records the maximum number of client fds opened in one pass.
- `stress_sockmany_cleanup()` shuts down and closes an array of sockets.
- `stress_sockmany_client()` opens up to `SOCKET_MANY_FDS` client sockets, connects each to the server, receives a small buffer, updates the shared maximum, and then closes all opened sockets.
- `stress_sockmany_server()` binds/listens on the per-instance port, accepts clients, sends `sockmany-max-size` bytes, applies TCP timeout/sync/quickack options when available, and increments bogo operations.
- `stress_sockmany()` parses `sockmany-if`, `sockmany-max-size`, and `sockmany-port`, validates the interface, reserves the port, creates shared state, forks, and cleans up.

## Control Flow

The entry point installs child and `SIGPIPE` handlers, reads options with maximize/minimize handling for max payload size, validates an optional interface, reserves a per-instance IPv4 port, and mmaps a shared `stress_sock_fds_t`. After synchronization it forks. The child runs the client on the same CPU as the parent, while the parent runs the server and kills the child when done.

The client initializes its local fd array to `-1`, then tries to create and connect sockets until the global continue flag clears or resource limits are hit. Expected resource conditions such as `EMFILE`, `ENFILE`, `ENOBUFS`, `ENOMEM`, `EADDRNOTAVAIL`, and `ECONNREFUSED` end the current batch rather than failing the stressor. Each connected socket receives a buffer, and the batch is then closed. The server creates a listening socket with `SO_REUSEADDR`, optional TCP retry/timeout tuning, and bind retry on `EADDRINUSE`. It accepts one client at a time, validates socket name/buffer paths, optionally sets `TCP_QUICKACK`, sends the configured payload, closes the accepted fd, and increments the bogo count.

## State and Persistence Behavior

The only shared state is the anonymous shared mmap used to report `max_fd` from client to parent. It also uses stress-ng's port reservation table and transient TCP sockets. No persistent files or network configuration changes are made.

## Dependencies and Integration Points

The file uses stress-ng network interface/address/port helpers, mmap helpers, signal helpers, affinity helpers, and kill helpers. It depends on IPv4 TCP sockets, optional `TCP_SYNCNT`, `TCP_USER_TIMEOUT`, `TCP_QUICKACK`, and `SO_REUSEADDR`. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

Opening up to 100,000 sockets is intentionally resource-heavy and may quickly hit fd, memory, socket buffer, or ephemeral port limits. Those limits are mostly treated as normal end-of-batch conditions. The client uses a static local fd array and a shared maximum index, so reported "sockets opened" is the highest index, not necessarily a count including zero. Interface validation falls back to loopback if the requested interface does not support AF_INET. The server uses a small listen backlog relative to the possible client burst, so connection refusal can be expected.

## Test Signals

Expected test signals include successful default loopback runs, controlled resource-limit exits without failure, correct max-socket debug reporting, and no unclosed fds after cleanup. Option tests should cover `--sockmany-max-size 1`, maximize/minimize, invalid interface fallback, and explicit port reservation conflicts.
