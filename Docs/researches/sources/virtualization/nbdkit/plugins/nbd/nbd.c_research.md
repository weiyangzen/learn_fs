# File Research: sources/virtualization/nbdkit/plugins/nbd/nbd.c

## Purpose
Implements the `nbd` plugin, which turns nbdkit into a forwarding NBD client backed by libnbd. It connects to another NBD server by URI, Unix socket, TCP, VSOCK, socket activation command, or pre-opened socket fd, then exposes the remote export through nbdkit callbacks.

## Main Entry Points
- `nbdplug_config()` parses connection mode, export selection, retry, shared connection mode, and TLS options.
- `nbdplug_config_complete()` validates mutually exclusive connection parameters, sets defaults, checks libnbd feature availability, and finalizes TLS/export behavior.
- `nbdplug_after_fork()` creates the shared handle after nbdkit forks when `shared=true` or when command/socket-fd implies sharing.
- `nbdplug_open_handle()` creates a libnbd handle, negotiates the export, configures TLS/meta contexts/full-info behavior, retries connection, and starts the reader thread.
- `nbdplug_reader()` drives the libnbd asynchronous state machine with `poll()` and a wake pipe.
- `nbdplug_pread()`, `nbdplug_pwrite()`, `nbdplug_zero()`, `nbdplug_trim()`, `nbdplug_flush()`, `nbdplug_extents()`, and `nbdplug_cache()` translate nbdkit requests into libnbd AIO commands.
- Capability callbacks forward remote server properties: size, block size, read-only, flush, trim, zero, FUA, multi-conn, cache, rotational, and base allocation extents.

## Internal Mechanics
Each `struct handle` owns one libnbd handle, a nonblocking pipe, a readonly flag, and a reader thread. Synchronous nbdkit callbacks are implemented by submitting libnbd AIO commands, storing completion state in a per-request `struct transaction`, kicking the reader thread, then waiting on a semaphore until the libnbd completion callback posts.

The plugin supports static export names and dynamic export pass-through via `nbdkit_export_name()`. With dynamic exports and URI connections it may use libnbd opt mode to postpone `NBD_OPT_GO` until the client export name is known. Export listing and default-export discovery use `NBD_OPT_LIST` and `NBD_OPT_INFO` when the build has the required libnbd APIs.

## Dependencies
Depends on libnbd, pthreads, POSIX pipes/poll/socket APIs, semaphores, nbdkit plugin API v2, and local helpers for string vectors, cleanup, byte swapping, and utility parsing.

## Risks and Notes
`shared=true` routes all nbdkit clients through one libnbd connection while the plugin advertises the remote multi-conn property separately; correctness depends on libnbd and the remote server tolerating concurrent AIO operations on that shared handle. Dynamic export mode is intentionally incompatible with shared connections. The reader thread lifecycle is central: command callbacks block on semaphores, so any reader thread exit makes later operations fail or stall depending on libnbd state. `socket-fd` ownership is delegated to libnbd through `nbd_connect_socket`, so configuration using an fd is inherently process/lifetime sensitive.
