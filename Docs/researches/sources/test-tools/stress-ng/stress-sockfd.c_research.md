# sources/test-tools/stress-ng/stress-sockfd.c

## Purpose

`stress-sockfd.c` implements `sockfd`, a Linux stressor that sends file descriptors over AF_UNIX sockets using `SCM_RIGHTS`. It exercises ancillary data construction/parsing, descriptor pressure, descriptor reuse between sender and receiver, Unix socket addressing, and cleanup of many fds.

## Important APIs, Types, and Functions

- `stress_socket_fd_send()` builds a `sendmsg()` call with one byte of data and a `SOL_SOCKET` / `SCM_RIGHTS` control message containing `fd_send`.
- `stress_socket_fd_recv()` receives one message, validates the marker byte, rejects truncated control data, and extracts the passed fd from `CMSG_DATA`.
- `stress_socket_client()` connects to the AF_UNIX server, receives up to `max_fd` descriptors, optionally sends descriptors back when `sockfd-reuse` is active and `select()` is available, tries to read pending bytes via `FIONREAD`, then closes the received descriptor array.
- `stress_socket_server()` binds/listens on the AF_UNIX address, accepts clients, repeatedly opens `/dev/zero`, sends the fd, closes the local copy, sends an invalid fd to exercise receiver handling, and increments bogo operations.
- `stress_sockfd()` computes descriptor limits, reserves a per-instance Unix socket port/name, allocates the fd array, forks client/server, and releases resources.

## Control Flow

The entry point installs `SIGCHLD`, reads `sockfd-port` and `sockfd-reuse`, reserves a per-instance port, determines the file descriptor limit, caps it for root and at one million descriptors, allocates an integer array, synchronizes, and forks. The child lowers OOM protection, enables failure injection, and runs the receiver. The parent runs the sender, then signals the child with `SIGALRM` and waits.

The server creates an AF_UNIX stream socket, enables `SO_REUSEADDR`, binds to a stress-ng-generated address, and listens. For each accepted connection it loops up to `max_fd`, optionally checks if the peer returned a reusable descriptor with `select()`, otherwise opens `/dev/zero`, sends that descriptor via `SCM_RIGHTS`, closes it locally, sends one bad fd, increments messages and bogo operations, and continues. The client connects with retry, receives descriptors into the allocated array, optionally returns them to the server, probes readable data with `FIONREAD`, closes all received fds, and removes the Unix socket path on cleanup.

## State and Persistence Behavior

Runtime state includes the allocated fd array, AF_UNIX socket path, opened `/dev/zero` descriptors, and stress-ng port reservation. Descriptor ownership is intentionally transferred between processes through kernel ancillary-data semantics. No files are persistently written; the Unix socket path is unlinked on both client/server cleanup paths when available.

## Dependencies and Integration Points

The implementation is Linux-only and depends on AF_UNIX, `sendmsg()`/`recvmsg()` control messages, `CMSG_*` macros, stress-ng network address helpers, out-of-memory adjustment, signal helpers, and fd cleanup helpers. Optional `select()` enables descriptor reuse. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`, with `sockfd-port` and `sockfd-reuse` options; non-Linux builds export unimplemented.

## Risks and Edge Cases

The stressor can open and pass a very large number of descriptors; root runs are deliberately given headroom to avoid exhausting the whole process. Ancillary data can fail with expected pressure errors such as `ETOOMANYREFS`, `ENOMEM`, `EPIPE`, and reset conditions. The server does not explicitly call `stress_net_release_ports()` at the end in this file, so correctness relies on process-local reservation cleanup elsewhere or the reservation being only a coordination guard. AF_UNIX path unlinking happens in helpers, but double unlink is harmless.

## Test Signals

Useful tests include default descriptor passing, `--sockfd-reuse`, low file-limit environments, root and non-root runs, and builds without `select()`. Expected behavior is bogo increments per successful descriptor send, no leaked fds after client cleanup, and graceful handling of pressure-related `sendmsg()` errors.
