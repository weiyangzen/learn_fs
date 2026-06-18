# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonkrpc.c

## Purpose

`nfs_commonkrpc.c` implements the common kernel RPC transport layer used by the FreeBSD NFS client, NFS callbacks, upcalls, pNFS data-server calls, and NFSv4.1 session-aware request handling. It creates and tears down krpc clients, selects authentication, sends mbuf-based RPC calls, parses common reply framing, manages NFSv4 sequence slots, handles retry/backoff/recovery cases, tracks server down/up notifications, and provides signal-interrupt helpers for interruptible mounts.

## Global State And Sysctls

The file defines DTrace probe hooks for NFSv2/3/4 client RPC start/done events when KDTrace is enabled. It declares shared NFS locks, statistics, request queues, callback pools, and client-state globals. Tunables include:

- `vfs.nfs.bufpackets` for socket buffer reservation scaling.
- `vfs.nfs.reconnects` for reconnect count.
- `vfs.nfs.nfs3_jukebox_delay`.
- `vfs.nfs.skip_wcc_data_onerr`.
- `vfs.nfs.dsretries` for pNFS data-server RPC retry limits.

`nfscl_use_gss[]` marks which NFSv4 operations should use RPCSEC_GSS under security modes such as `syskrb5`.

## Connection Management

`newnfs_connect()` creates an RPC client for a mount, callback, upcall, or pNFS DS connection. It temporarily installs the mount/socket credential as the current thread credential because low-level socket setup may use `td_ucred`. It chooses `udp`, `tcp`, `udp6`, or `tcp6` netconfig entries from the target address and socket type, probes socket buffer reservations with `soreserve()`, clamps `bufpackets` between 2 and 64, and emits guidance when `kern.ipc.maxsockbuf` is too small for large TCP NFS I/O.

For client mounts it configures interruptibility, reserved ports, TLS/certificate options, hard/soft retry counts, UDP retry timeout, and NFSv4/pNFS timeout behavior. For NFSv4.1 client connections it may attach a callback backchannel when callback daemons are running. For DS connections (`cred == NULL`) it sets shorter timeouts and `dsretries` so failed data servers are detected. For callbacks/upcalls (`nmp == NULL`) it selects callback or upcall retry behavior and optional TLS. The created `CLIENT` is installed under `nr_mtx`; if another thread connected first, the local client is released.

`newnfs_disconnect()` atomically detaches the primary client and any `nconnect` auxiliary clients, purges GSS security state in the credential's vnet, closes, and releases all RPC clients.

## Authentication

`nfs_getauth()` returns an RPC AUTH handle for AUTH_SYS or RPCSEC_GSS Kerberos flavors. For Kerberos it maps security flavor to GSS service (`none`, `integrity`, or `privacy`), obtains the Kerberos mechanism OID when needed, and either finds an existing security context for a server principal or creates one using an explicit client principal. AUTH_SYS falls back to `authunix_create()`.

`newnfs_request()` chooses credentials and authentication based on callback/client direction, mount security flags, `ND_USEGSSNAME`, system uid configuration, root credential fallback, server principal storage in `nfssockreq`, and operation-specific `nfscl_use_gss[]` policy.

## Request Path

`newnfs_request()` is the central RPC engine. It rejects new requests during forced unmount, holds the authentication credential, masks interruptible-mount signals around the RPC if needed, ensures the primary connection exists, optionally selects an `nconnect` auxiliary TCP connection for large read/write/readdir RPCs, sets feedback callbacks, maps NFSv4 procedures to `COMPOUND`, maps NFSv3 logical proc numbers to NFSv2 proc numbers when needed, and allocates a lightweight outstanding request record for NFSv4 compound operations requiring recovery suppression.

It then sends the request via:

- `clnt_bck_call()` for backchannel callback calls tied to a session transport,
- `CLNT_CALL_MBUF()` on an auxiliary `nconnect` client for large data calls,
- or `CLNT_CALL_MBUF()` on the primary `nfssockreq` client.

The current thread credential is temporarily changed to the auth credential during `CLNT_CALL_MBUF()` because RPC auth refresh may require the correct vnet.

RPC status is translated to kernel errors. Timeouts increment stats and become `ETIMEDOUT`; version mismatch becomes protocol errors; send/receive/system errors may free or poison NFSv4.1 session slots; auth errors become `EACCES`. Successful replies are realigned for strict-alignment architectures, then the descriptor mbuf cursors are initialized.

## NFSv4 And Session Handling

For NFSv4 replies, `newnfs_request()` strips the compound tag, reads operation count and first op/status, and handles `SEQUENCE` or `CBSEQUENCE` results. It verifies session IDs, slot IDs, returned sequence numbers, and target/highest slot values. It adjusts the session's fore-channel slot count, resets unused slot sequence values when the server lowers slot availability, records bad slots on mismatches or `NFSERR_SEQMISORDERED`, and frees slots after use.

`NFSERR_BADSESSION` on a client MDS RPC marks the MDS session defunct, initiates recovery when appropriate, sleeps briefly for a new session, optionally rewrites the request's SEQUENCE fields when `ND_LOOPBADSESS` is set, and retries. Delay/grace/resource/retryable uncached reply errors use exponential sleep capped by `NFS_TRYLATERDEL`; if a sequence slot was consumed, its sequence number is incremented and patched into the request before retry.

The code marks `ND_INCRSEQID` for open/confirm/downgrade/close/lock/locku operations when their reply status requires advancing the open/lock owner sequence. It also sets `ND_NOMOREDATA` for most failed NFSv4 operations and maps stale recovery errors to `NFSERR_STALEDONTRECOVER` when the outstanding request was marked `R_DONTRECOVER`.

## Cancellation, Signals, And Notifications

`newnfs_nmcancelreqs()` closes the primary mount client, auxiliary `nconnect` clients, and DS clients on all non-MDS sessions so forced unmounts or teardown can terminate outstanding RPCs.

`newnfs_set_sigmask()`, `newnfs_restore_sigmask()`, `newnfs_msleep()`, and `newnfs_sigintr()` implement the signal behavior for `NFSMNT_INT` mounts. Only a narrow signal set (`SIGINT`, `SIGTERM`, `SIGHUP`, `SIGKILL`, `SIGQUIT`) is allowed to interrupt NFS operations, while already-masked or ignored signals remain masked.

`nfs_feedback()`, `nfs_down()`, and `nfs_up()` produce rate-limited terminal messages and VFS event notifications (`VQ_NOTRESP`, `VQ_NOTRESPLOCK`) when servers stop responding or recover.

`nfs_resetslots()` clears sequence numbers for nonbusy slots above the current fore-channel slot limit.

## Dependencies

This file depends on FreeBSD krpc (`CLNT_CALL_MBUF`, `clnt_reconnect_create`, `CLNT_CONTROL`), RPCSEC_GSS, sockets, credentials/vnets, NFS mount/session/client state, NFS descriptor/XDR macros, DTrace hooks, vfs event signaling, task/callback infrastructure, and NFS recovery/session helpers such as `nfsv4_freeslot()`, `nfsv4_sequencelookup()`, and `nfsmnt_mdssession()`.

## Invariants And Risks

- `nd_mreq` is always consumed/freed by `newnfs_request()`, including error paths.
- Current thread credentials are deliberately swapped during connect/auth/RPC refresh and must always be restored.
- NFSv4.1 session slot sequence numbers are fragile; failed sends, bad slots, wrong slots, and retries must not allow stale cached replies to be accepted.
- Retry behavior differs by operation because non-idempotent NFSv4 operations cannot always be replayed safely.
- `nconnect` sends only selected large-message operations over auxiliary connections to avoid head-of-line blocking for small metadata RPCs.
- GSS auth handles cached in `nfssockreq` must not be destroyed by request cleanup, while per-request auth handles must be destroyed.
