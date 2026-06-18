# sources/test-tools/stress-ng/stress-sock.c

## Purpose

`stress-sock.c` implements the main `sock` stressor. It creates a forked client/server pair and exercises socket creation, connection setup, send/receive APIs, socket options, ioctls, TCP options, port reservation, interface selection, and optional zero-copy sends. It supports multiple domains, socket types, protocols, and send/receive methods, with metrics for message rate and queue depth.

## Important APIs, Types, and Functions

- `stress_sock_options_t` maps user-facing method/type/protocol names to numeric constants.
- `sock_options_opts`, `sock_options_types`, and `sock_options_protocols` back the `sock-opts`, `sock-type`, and `sock-protocol` option parsers.
- `stress_get_congestion_controls()` reads `/proc/sys/net/ipv4/tcp_allowed_congestion_control` and returns congestion-control names for optional TCP testing.
- `stress_sock_ioctl()` exercises socket-related ioctls such as ownership, interface config, timestamps, namespace fd, and Unix socket backing-file queries.
- `stress_sock_invalid_recv()` intentionally calls `recv`, `recvmsg`, and `recvmmsg` with invalid flags or fds.
- `stress_sock_client()` connects to the server, exercises get/set socket options and receive paths, samples input queue metrics, and unlinks AF_UNIX socket paths.
- `stress_sock_server()` binds/listens, accepts clients, sends data through `send`, `sendmsg`, or `sendmmsg`, samples output queue metrics, and kills the client on cleanup.
- `stress_sock_kernel_rt()` detects PREEMPT_RT kernels and avoids some ownership ioctls when realtime behavior could be sensitive.
- `stress_sock()` parses options, validates interfaces, reserves a port, allocates the shared I/O buffer, forks the client, and runs the server.

## Control Flow

The entry point installs a `SIGCHLD` handler, loads settings for domain, interface, port, zero-copy, send method, socket type, and protocol, and adjusts protocol to zero for AF_UNIX. It validates the requested interface and reserves a wrapped per-instance port through stress-ng's network port allocator. It installs a `SIGPIPE` stop handler, mmaps a 64 KiB anonymous I/O buffer, synchronizes start, and forks.

The child applies failure-injection setup, pins to the parent CPU, and runs `stress_sock_client()`. The client loops over socket creation, deliberately tries invalid socket arguments, connects with retries, optionally enables zero-copy, randomizes TCP congestion control for IPv4, exercises IP/TCP/SOL_SOCKET get/set paths, then receives data using the method corresponding to the selected sender. It periodically samples `FIONREAD`/`SIOCINQ`, calls invalid receive helpers, and records average queued input bytes.

The parent runs `stress_sock_server()`. The server creates a socket, enables `SO_REUSEADDR`, deliberately tests invalid `setsockopt()` combinations, binds/listens with retry on `EADDRINUSE`, optionally mmaps the socket fd just to exercise that path, and accepts connections. For each accepted socket it checks names, socket buffer sizes, optional TCP quickack/nodelay, fills the shared buffer, and sends a configured number of message batches. It periodically samples `SIOCOUTQ`, reads fdinfo, runs socket ioctls, closes the accepted fd, and records messages per second plus average output queue length. Cleanup closes sockets, unmaps buffers, unlinks AF_UNIX paths, kills the child, and releases the reserved port.

## State and Persistence Behavior

The stressor persists no repository or user data. Runtime state includes a shared anonymous mmap buffer inherited across fork, reserved network port state maintained by stress-ng, transient AF_UNIX socket paths, and per-run metrics. It reads but does not write `/proc/sys/net/ipv4/tcp_allowed_congestion_control`. It can change socket-local options extensively, but those changes are per-fd.

## Dependencies and Integration Points

The file integrates with stress-ng network helpers (`stress_net_sockaddr_if_set`, `stress_net_interface_exists`, port reserve/release, domain names), signal helpers, affinity helpers, mmap/madvise helpers, fdinfo readers, and metrics. It depends on standard socket APIs, Linux socket ioctls, TCP headers, Unix-domain socket headers, and optional `sendmsg`, `sendmmsg`, `recvmsg`, `recvmmsg`, `MSG_ZEROCOPY`, and `SO_ZEROCOPY`. The exported stressor is `CLASS_NETWORK | CLASS_OS | CLASS_IPC`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

The main risks are resource exhaustion, flaky kernel-option availability, and network namespace/interface assumptions. Port reservation mitigates instance collisions but bind can still hit `EADDRINUSE` and retries. Some socket options are read-only, privileged, or protocol-specific; failures are usually intentionally ignored, while core socket/connect/bind/listen failures are reported. AF_UNIX cleanup depends on the address helper returning a stable `sun_path`. Zero-copy enablement is best-effort and disables itself after a warning. `stress_get_congestion_controls()` returns pointers into a static buffer plus a heap pointer array, so consumers must not outlive the static buffer contents.

## Test Signals

Useful test coverage includes default IPv4 stream TCP, AF_UNIX, random send method, `sendmsg`/`sendmmsg` builds, `--sock-nodelay`, invalid interface fallback, MPTCP availability when compiled, and `--sock-zerocopy` on kernels with and without support. Expected metrics are "messages sent per sec", "byte average out queue length", and "byte average in queue length"; successful runs should release ports and leave no AF_UNIX socket path behind.
