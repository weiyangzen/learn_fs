# File Research: sources/local-fs/e2fsprogs/misc/uuidd.c

## Purpose
Implements `uuidd`, a Unix-domain socket daemon and command-line client for generating libuuid random, time-based, and bulk UUID responses.

## Key Elements
Command-line parsing supports daemon/debug mode, kill mode, random/time test requests, bulk count, custom pidfile/socket path, quiet mode, and idle timeout. Non-root invocations that use client/debug/custom-path operations drop effective IDs back to the real user/group.

Client requests use `call_daemon`, which connects to the configured Unix socket, sends a one-byte operation plus optional count, reads a 32-bit reply length, validates it against the caller buffer, and returns UUID bytes, counts, pid text, or max-operation text depending on operation.

`server_loop` owns daemon startup. It creates and locks the pidfile, probes for an existing daemon, binds/listens on the Unix socket, optionally daemonizes, installs cleanup signal handlers, writes its pid, accepts client connections, decodes operations, and dispatches to libuuid internal generators. Bulk time requests return one UUID plus a count of subsequent UUIDs; bulk random requests cap count to 1000 and fit the fixed reply buffer.

`create_daemon` forks, exits the parent, redirects stdio to `/dev/null`, changes to `/`, creates a new session, and sets real/effective uid to the effective uid. `read_all` and `write_all` provide retrying I/O loops for EINTR/EAGAIN-style partial transfers. Signal cleanup unlinks pidfile and socket.

## Dependencies
Uses libuuid public and internal APIs (`uuid__generate_time`, `uuid__generate_random`), `uuid/uuidd.h` operation constants and default paths, Unix sockets, file locks, pid files, signals, privilege APIs, NLS setup, and ext2fs headers for portability attributes.

## Behavior/Risks
The protocol is intentionally small but binary and host-endian for counts/reply lengths. Socket `bind` uses the caller-provided path copied into `sun_path` and unlinks any existing path first. The daemon uses a fixed 1024-byte reply buffer and caps bulk random replies accordingly. Cleanup relies on signal paths; abnormal termination can leave stale socket/pidfile entries, though startup probes and pidfile locking reduce duplicate-daemon risk.
