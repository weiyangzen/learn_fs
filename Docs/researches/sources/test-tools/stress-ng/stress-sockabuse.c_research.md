# sources/test-tools/stress-ng/stress-sockabuse.c

## Purpose

`stress-sockabuse.c` implements `sockabuse`, a socket misuse and abuse stressor. It builds a normal IPv4 client/server pair but also applies many file, xattr, mmap, fcntl, ioctl, and socket-option operations to socket file descriptors, and cycles through a broad set of socket domains and types to probe kernel error paths.

## Important APIs, Types, and Functions

- `sockabuse_domains`, `sockabuse_types`, and `sockabuse_sockopts` are compile-time arrays of available address families, socket types, and `SOL_SOCKET` options.
- `sockabuse_domain_type_flags` records which domain/type combinations still appear usable so the stressor can stop retrying combinations that fail.
- `stress_sockabuse_socket()` iterates through domain/type combinations, opens sockets with protocol zero and random protocols, and updates the flags.
- `stress_sockabuse_sockopts()` rotates through `getsockopt(SOL_SOCKET, option)` calls on a supplied fd.
- `stress_sockabuse_fd()` deliberately applies inappropriate file operations to a socket fd: `fdatasync`, `fsync`, `fallocate`, `fchdir`, `fchmod`, `fchown`, `flock`, xattr calls, `ftruncate`, `lseek`, pidfd signal, mmap, copy-file-range, fadvise, and sync-file-range.
- `stress_sockabuse_client()` connects and receives one buffer, then abuses the connected fd.
- `stress_sockabuse_server()` repeatedly binds/listens/sends one buffer to accepted clients, abuses accepted and listening fds, and updates throughput metrics.
- `stress_sockabuse()` handles option parsing, port reservation, signal setup, fork, and cleanup.

## Control Flow

The entry point initializes all domain/type flags to enabled, installs child and `SIGPIPE` handlers, reads `sockabuse-port`, reserves a per-instance IPv4 port, synchronizes, and forks. The child runs the client loop on the same CPU as the parent. The parent runs the server and kills the child on completion.

The client repeatedly opens an IPv4 stream socket, resolves the server address, retries connection with increasing backoff, receives a fixed 8 KiB buffer, abuses the fd with general file operations and socket options, then shuts down and closes it. The server repeatedly opens a listening IPv4 stream socket, enables `SO_REUSEADDR`, binds/listens, accepts up to sixteen client sockets per listener instance, sends an 8 KiB pattern buffer, abuses the accepted socket and the listening socket, closes them, and calls `stress_sockabuse_socket()` to exercise unrelated socket-family/type construction paths. Bogo operations increment once per server listener cycle.

## State and Persistence Behavior

The stressor uses process-local static state to remember domain/type combinations that have failed. It creates no persistent files, but it may call xattr and file-like syscalls against socket fds and may invoke mmap attempts on them. Network port reservation state is maintained by stress-ng and released at the end. Runtime metrics record messages per second.

## Dependencies and Integration Points

The file depends on stress-ng networking, affinity, signal, kill, builtin, and fd shim helpers. Platform features are heavily conditional: many address families, `SO_*` options, `flock`, xattr APIs, `futimens`, `FIONREAD`, `copy_file_range`, `pidfd_send_signal`, `posix_fadvise`, and sync-file-range are included only when available. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`, with `sockabuse-port` as its only option.

## Risks and Edge Cases

This stressor intentionally sends invalid operations to socket fds; most failures are expected and ignored. It can generate noisy kernel paths on systems with unusual protocol modules or restricted address families. The static domain/type flag array is mutable and process-local, so it adapts during a run but is not shared across forked processes. Some file operations can be permission-sensitive or return platform-specific errors; the code intentionally does not treat those as failures. Port bind loops can spin through `EADDRINUSE` until the global continue flag clears.

## Test Signals

Expected signals include successful client/server message exchange, bogo increments, and "messages sent per sec" metric. Runs should tolerate missing optional APIs through compile-time guards. Port exhaustion should produce skip/no-resource behavior rather than unbounded failure. Kernel logs should be monitored when adding new abuse operations because this stressor is intended to exercise unusual syscall combinations.
