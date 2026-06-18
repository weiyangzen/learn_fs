# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/rpc.c

## Purpose
`rpc.c` provides a custom TCP ONC RPC client for PROXY_V3. It avoids using standard client helpers because Ganesha's server-side RPC integration conflicts with making nested NFS client calls. It manages a reusable socket/buffer pool, AUTH_UNIX construction, XDR call/reply encoding, record markers, portmapper discovery, and program-specific wrappers for NFS v3, MOUNT v3, and NLM v4.

## Important APIs, Types, And Functions
Global state includes `global_xid`, `rpcMachineName`, `rpcLock`, `rpcNumSockets`, and `fd_entries`. `struct rpc_buf` is a growable byte buffer per pool entry. `struct fd_entry` tracks in-use/open state, endpoint identity, fd, and RPC buffer.

`proxyv3_rpc_init()` initializes hostname, mutex, socket pool, random XID seed, and one-time state. `proxyv3_openfd()` validates IPv4/IPv6 sockaddr inputs, binds a reserved client port under lock, sets the target port, and connects TCP. `proxyv3_fd_is_open()` probes a cached socket with nonblocking peek. `proxyv3_getfdentry()` and `proxyv3_getfd_blocking()` acquire a pool slot, reuse matching sockets, open new sockets, and back off when the pool is full. `proxyv3_release_fdentry()` returns or force-closes a slot. `proxyv3_call()` is the core RPC engine. Wrappers are `proxyv3_nfs_call()`, `proxyv3_mount_call()`, `proxyv3_nlm_call()`, and `proxyv3_find_ports()`.

## Control Flow
A call acquires an fd entry for host/port, creates AUTH_UNIX credentials from passed user credentials or defaults, XDR-encodes an RPC call into the entry buffer after a TCP record marker slot, writes the record marker and payload, destroys auth, reads the response marker and XID, validates the XID and length, resizes the buffer for the full reply, decodes `xdr_replymsg()` with the caller's decode function wired as accepted results, frees only reply wrapper allocations, releases the fd entry for reuse, and returns whether decode and RPC accept status succeeded.

Port discovery loops over MOUNT, NFS, and NLM pmap queries to `PMAPPORT`, using unauthenticated PMAP RPC calls and storing returned TCP ports.

## State And Persistence
State is process-global and lives until module unload/process exit. Sockets remain open across calls when reusable and are force-closed on transport/protocol errors. Buffers are lazily allocated based on current `PROXY_V3.module.fs_info.maxwrite + 512` and grow to larger replies as needed. The pool size is configured by `num_sockets`.

## Dependencies And Integration Points
The file depends on ONC RPC/XDR headers, portmap definitions, sockets, Ganesha allocation/logging, generated NFS/MOUNT/NLM constants, `PROXY_V3` fsinfo, and `proxyv3_fsal_methods.h`. All high-level PROXY_V3 filesystem and lock operations depend on these wrappers for backend communication.

## Risks
The transport uses blocking `connect`, `read`, and `write` without explicit timeouts, so backend stalls can tie up worker threads and pool entries. Partial `read()` returning zero is not specially handled in the reply-body loop and can spin if EOF occurs after the header. `inet_ntop()` is called with the whole sockaddr pointer rather than the address field, which can produce misleading diagnostics or fail. The code assumes single-fragment RPC replies by clearing the high record-marker bit and does not process multi-fragment records. If `xdr_callmsg()` or arg encoding fails, `xdr_destroy()` is not called on the XDR stream. Pool cleanup at module unload is absent in this file. Reserved-port binding serializes under `rpcLock` and can fail under privilege/container restrictions.

## Test Signals
Transport tests should simulate full and partial writes, short reads, EOF after header, mismatched XID, rejected RPC replies, auth failures, large READDIR replies requiring buffer growth, stale reusable sockets, pool exhaustion/backoff, IPv4/IPv6 addresses, unprivileged bind failure, and portmapper missing services. Integration tests should confirm all wrappers use the correct program/version/procedure numbers.
