# File Research: sources/os/linux/linux/fs/smb/server/server.c

This file is the ksmbd module lifecycle, control-plane, and request-dispatch hub.

Global state:
- Defines `ksmbd_debug_types`.
- Defines global `struct ksmbd_server_config server_conf`.
- Provides setters/getters for NetBIOS name, server string, and workgroup.
- Initializes server defaults: starting state, min/max protocol, NTLMSSP auth, optional Kerberos mechanisms, and max inflight request credits.

Request handling:
- `queue_ksmbd_work()` initializes SMB protocol state for a connection, allocates work, transfers `conn->request_buf`, queues the work, increments request count, and updates activity.
- `__handle_ksmbd_work()` decrypts transform requests, allocates response buffers, initializes response headers, checks session/tree connection, dispatches commands, assigns credits, signs responses, updates preauth hash, encrypts responses when needed, releases tcon/session refs, and writes the response.
- `__process_request()` verifies SMB messages, validates command dispatch entries, checks signatures, invokes the command handler, increments command counters, and supports positive return values for chained/AndX-style dispatch.
- Connection termination deregisters sessions and destroys leases for that connection.

Control work:
- Server control work supports init and reset.
- Init resets proc counters and starts connection transport.
- Reset performs IPC soft reset, transport destroy, durable scavenger stop, config free/reinit, and returns to startup state.
- Work items hold a module reference until completion and serialize through `ctrl_lock`.

Sysfs class:
- Registers `ksmbd-control` with `stats`, `kill_server`, and `debug` attributes.
- `stats` exposes a versioned state/port/ipc activity line.
- `kill_server` accepts `hard` and performs synchronous reset.
- `debug` toggles debug categories or all categories.

Module lifecycle:
- Init registers class, initializes procfs and session proc entries, registers TCP callbacks, initializes config, work pools, file cache, IPC, global file table, inode hash, crypto, request workqueue, and connection workqueue.
- Exit sets shutdown state, tears down procfs, sysfs, workqueues, IPC, transports, crypto, file table, leases, file cache, and inode hash, using `rcu_barrier()` before destroying deferred connection workqueue state.

Role in this group:
- Uses `server.h` for global config.
- Uses `oplock.h` for lease cleanup.
- Uses `user_session.h` for session deregistration and ref release.
- Dispatch behavior depends on protocol ops/tables defined in `smb2ops.c`.
