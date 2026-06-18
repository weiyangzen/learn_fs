# sources/test-tools/fio/server.c

## Purpose
`server.c` implements fio's client/server transport endpoint. It listens on TCP, IPv6, or Unix-domain sockets, accepts client connections, parses network commands, starts backend jobs, forwards text/statistics/disk-util/log data back to the client, and supports daemon pidfile mode. It is a central integration point between fio's job parser/backend, shared-memory allocator, statistics subsystem, verify-state exchange, disk-util reporting, and optional zlib log compression.

## Important APIs, Types, And Functions
The file exports `fio_start_server()`, `fio_server_text_output()`, `fio_net_send_cmd()`, `fio_net_send_simple_cmd()`, `fio_server_parse_string()`, `fio_server_parse_host()`, `fio_server_op()`, `fio_server_got_signal()`, `fio_net_recv_cmd()`, `fio_send_iolog()`, `fio_server_send_ts()`, `fio_server_send_gs()`, `fio_server_send_du()`, `fio_server_send_job_options()`, `fio_server_get_verify_state()`, `fio_server_send_add_job()`, `fio_server_send_start()`, `fio_net_send_quit()`, and pthread key setup/destruction helpers. Internally, `struct sk_entry` represents queued outbound commands and linked vector fragments; `struct fio_fork_item` tracks connection/job child processes or Windows handles; `struct cmd_reply` synchronizes sendfile/verify-state replies.

The core wire helpers are `__fio_init_net_cmd()`, `fio_init_net_cmd()`, `fio_net_cmd_crc()`, `verify_convert_cmd()`, `fio_recv_data()`, `fio_sendv_data()`, and `fio_net_recv_cmd()`. They enforce little-endian protocol fields, command CRCs, payload CRCs, payload fragment limits, and protocol version matching. `fio_net_recv_cmd()` also defragments commands marked `FIO_NET_CMD_F_MORE` and null-terminates text/job buffers after receipt.

Connection lifecycle is handled by `fio_server()`, `fio_init_server_connection()`, `accept_loop()`, `handle_connection()`, `handle_command()`, and `handle_run_cmd()`. Outbound asynchronous sending is managed through `sk_out_assign()`, `sk_out_drop()`, `fio_net_queue_cmd()`, `fio_net_queue_entry()`, `handle_xmits()`, `handle_sk_entry()`, `send_vec_entry()`, and `finish_entry()`.

## Control Flow
Startup enters `fio_start_server()`. Without a pidfile it calls `fio_server()` directly; with a pidfile it checks for an existing live server, forks into a daemon, redirects standard streams to `/dev/null`, enables syslog logging, and unlinks the pidfile on exit. `fio_server()` parses the configured bind argument, installs signal handlers, opens the listening socket, and enters `accept_loop()`.

For each accepted connection, Unix builds fork a child and Windows starts a child process through a pipe/duplicated socket. The child assigns the connection `sk_out` to thread-specific storage, then `handle_connection()` repeatedly flushes outbound queue entries, polls for inbound commands, receives one `fio_net_cmd`, and dispatches it. Job definition commands call `parse_jobs_ini()` or `parse_cmd_line()` and then send `FIO_NET_CMD_START`; `FIO_NET_CMD_RUN` forks/runs `fio_backend()`; `FIO_NET_CMD_SEND_ETA` sends ETA data; `FIO_NET_CMD_UPDATE_JOB` converts packed options into a running job; `FIO_NET_CMD_VTRIGGER` exports all I/O state, terminates threads, and executes the trigger.

When the fio backend is running in server mode, stats calls in other modules enqueue network messages. `fio_server_send_ts()` converts `thread_stat` and `group_run_stats`, appends optional per-priority latency arrays and steady-state ring buffers, and queues `FIO_NET_CMD_TS`. `fio_send_iolog()` builds a vector command: header first, then plain log chunks, pre-compressed chunks, or zlib-compressed chunks. `fio_server_send_du()` sends one disk-util PDU per disk.

## State And Persistence Behavior
Global state includes `fio_net_port`, `exit_backend`, `fio_server_arg`, `bind_sock`, socket address globals, zlib capability flags, the remote server name `me`, and the pthread-specific `sk_out_key`. `struct sk_out` holds a reference count, socket fd, semaphores, and a queued outbound list; reference count discipline is essential across connection children and backend children. `exit_backend` is the process-wide shutdown flag used by loops and send/recv retry paths.

Persistent filesystem state is limited to server pidfiles and Unix socket paths. `fio_start_server()` writes and later unlinks the pidfile in daemon mode; signal handling unlinks `bind_sock`. Verify-state transfer requests a file from the client via `FIO_NET_CMD_SENDFILE`, validates `verify_state_hdr`, copies only the `thread_io_list`, and stores it in caller-owned memory.

## Dependencies And Integration Points
This file depends heavily on `server.h`, `stat.h`, `diskutil.h`, `fio.h`, `options.h`, `verify-state.h`, `smalloc.h`, endian helpers, CRC16, semaphores, fork/wait or Windows process APIs, sockets, poll, and optional zlib. It is called by the fio backend/stat/logging layers whenever server-mode output is needed. It also consumes `thread_options_pack` conversion routines and fio global job/thread lists.

## Risks And Edge Cases
The protocol is bounded by `FIO_SERVER_MAX_FRAGMENT_PDU` and `FIO_SERVER_MAX_CMD_MB`, but the maximum command limit is very large and still relies on allocation success. Pointer arithmetic on `void *` is a GNU C assumption. `fio_server_parse_string()` mutates the supplied string when splitting on comma, so callers must pass mutable storage. `fio_server_send_ts()` must keep `thread_stat` layout and offset fields synchronized with client-side decode logic; packed structs with pointer/offset unions are ABI-sensitive. Asynchronous queue ownership depends on `SK_F_FREE`, `SK_F_COPY`, and `SK_F_VEC`; mismatched flags would leak or double-free memory. Signal handling is minimal and `fio_server_got_signal()` asserts that a `sk_out` exists. zlib histogram log sending mutates histogram entries by subtracting previous buckets before transfer.

## Test Signals
Useful tests are client/server probe/version mismatch tests, fragmented command CRC failure tests, job/jobline/load-file command round trips, ETA/update-job/verify-state reply tests, zlib and non-zlib iolog transfer tests, daemon pidfile conflict tests, Unix socket binding tests, IPv4/IPv6 parse tests, and process cleanup tests where job children exit by status or signal.
