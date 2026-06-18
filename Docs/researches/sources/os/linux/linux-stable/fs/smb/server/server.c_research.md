# File Research: sources/os/linux/linux-stable/fs/smb/server/server.c

This file is ksmbd’s main module and request-processing hub. It owns global server configuration, sysfs control, module lifecycle, transport callbacks, request dispatch, response signing/encryption, and server reset/init work.

Global state:
- `ksmbd_debug_types`: debug mask.
- `server_conf`: global `struct ksmbd_server_config`.
- `ctrl_lock`: serializes control work and hard reset.

Configuration helpers:
- `___server_conf_set()`
  - Replaces one of the global config strings.
- `ksmbd_set_netbios_name()`, `ksmbd_set_server_string()`, `ksmbd_set_work_group()`.
- `ksmbd_netbios_name()`, `ksmbd_server_string()`, `ksmbd_work_group()`.
- `server_conf_init()`
  - Sets state to starting, initializes protocol bounds, auth mechanisms, signing defaults, and max inflight requests.
- `server_conf_free()`
  - Frees config strings.

Request processing:
- `check_conn_state()`
  - Detects exiting/reconnect-needed connection and sets disconnected status.
- `__process_request()`
  - Verifies SMB message.
  - Extracts command.
  - Bounds-checks command index.
  - Rejects unimplemented commands.
  - Verifies request signature when required.
  - Dispatches command handler.
  - Increments request counters.
  - Handles positive return values as chained/AndX-style follow-up commands.
- `__handle_ksmbd_work()`
  - Handles transform-header decryption.
  - Allocates response buffer.
  - Initializes response header.
  - Checks user session and tree connection.
  - Processes one or more chained SMB2 messages.
  - Grants response credits.
  - Signs response when session/signing rules require it.
  - Releases tree/session references.
  - Updates SMB 3.1.1 preauth response hash.
  - Encrypts response when needed.
  - Writes response.
- `handle_ksmbd_work()`
  - Worker entry: increments request-served stat, handles request, dequeues/frees work, decrements connection request count.
- `queue_ksmbd_work()`
  - Initializes SMB dialect/server state for connection, allocates work, transfers request buffer ownership, queues work.
- `ksmbd_server_process_request()`
  - Transport callback wrapper.
- `ksmbd_server_terminate_conn()`
  - Deregisters sessions and destroys connection lease table.
- `ksmbd_server_tcp_callbacks_init()`
  - Registers process and terminate callbacks with connection layer.

Control work:
- `server_ctrl_handle_init()`
  - Resets proc counters, initializes connection transport, marks server running.
- `server_ctrl_handle_reset()`
  - Soft-resets IPC, destroys transport, stops durable scavenger, frees and reinitializes server config, marks starting.
- `server_ctrl_handle_work()`
  - Executes init/reset work under `ctrl_lock` and drops module reference.
- `server_queue_ctrl_init_work()`, `server_queue_ctrl_reset_work()`
  - Queue control work on `system_long_wq`.

Sysfs control:
- Class: `ksmbd-control`.
- `stats_show()`
  - Emits stats format version, state string, TCP port, and IPC activity time.
- `kill_server_store()`
  - Accepts `hard`, marks resetting, and performs reset synchronously under `ctrl_lock`.
- `debug_show()` / `debug_store()`
  - Show and toggle debug classes: `smb`, `auth`, `vfs`, `oplock`, `ipc`, `conn`, `rdma`, or all.

Module lifecycle:
- `ksmbd_server_init()`
  - Registers class.
  - Initializes proc and session proc support.
  - Registers TCP callbacks.
  - Initializes server config, work pools, file cache, IPC, global file table, inode hash, crypto, workqueue, connection workqueue.
  - Has staged error unwinding.
- `ksmbd_server_shutdown()`
  - Marks shutting down and destroys proc, sysfs class, workqueue, IPC, transport, crypto, global file table, leases, work pool, file cache, and config.
- `ksmbd_server_exit()`
  - Calls shutdown, waits for RCU callbacks, destroys connection workqueue, releases inode hash.

Risk areas:
- Request processing is reference-sensitive: tree connection and session references are released in the send path after possible encryption/signing.
- Error paths before `send:` must leave enough response state for `ksmbd_conn_write()` or intentionally return without writing.
- `kill_server_store()` directly calls reset handler while holding `ctrl_lock`; it mirrors queued reset logic but executes synchronously.
- Module teardown ordering matters because connection puts can defer release onto `ksmbd_conn_wq` after RCU callbacks.
