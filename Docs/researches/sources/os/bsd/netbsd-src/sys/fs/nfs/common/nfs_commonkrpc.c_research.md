# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonkrpc.c

## Purpose
Implements the main reconnecting RPC transport path used by the new NFS client and NFSv4 callback/upcall code. It manages RPC client creation, authentication, request execution, NFS reply parsing, NFSv4 sequence-slot handling, retry/backoff policy, interruptible mount signal handling, and server up/down notifications.

## Main Interfaces
- `newnfs_connect` creates/configures an RPC client for an `nfssockreq`, including socket buffer reservation sizing, reserved-port/connect behavior, soft/hard retry settings, UDP retry timeout, and optional NFSv4 backchannel setup.
- `newnfs_disconnect` purges GSS state, closes, and releases an RPC client.
- `newnfs_request` sends an NFS request mbuf, handles auth selection, RPC invocation, reply realignment/parsing, NFSv4 compound status handling, retryable errors, slot freeing, stale cache invalidation, DTrace probes, and cleanup.
- `newnfs_nmcancelreqs` closes an active client to cancel requests during forced unmount.
- `newnfs_set_sigmask`, `newnfs_restore_sigmask`, `newnfs_msleep`, and `newnfs_sigintr` implement signal handling for interruptible NFS mounts.

## Connection Behavior
- Temporarily switches thread credentials to mount/socket credentials while creating and configuring sockets.
- Selects `udp`, `tcp`, `udp6`, or `tcp6` netconfig based on address family and socket type.
- Preflights socket buffer reservation with `soreserve`, shrinking `nfs_bufpackets` scale if needed.
- Uses `clnt_reconnect_create` and sets wait channel, interruptibility, reserved-port use, retries, UDP retry timeout, and optional NFSv4.1 backchannel transport.
- Protects `nr_client` publication with `nr_mtx` so concurrent connect attempts do not install duplicate clients.

## Authentication
- `nfs_getauth` selects RPCSEC_GSS Kerberos modes (`krb5`, integrity, privacy) when requested, otherwise falls back to AUTH_SYS.
- `newnfs_request` chooses credentials from the caller, mount system credential, host principal, server principal, callback client flags, or NFSv4 system-operation flags.
- Cached host-principal auth may be stored in `nrp->nr_auth` and refreshed instead of destroyed per request.

## Request/Reply Flow
- Rejects requests during forced unmount and masks selected signals for interruptible client mounts.
- Connects lazily if no RPC client exists.
- Maps NFSv2 proc numbers through `nfsv2_procid`; NFSv4 non-null client calls use COMPOUND.
- Optionally records outstanding NFSv4 requests in `nfsd_reqq` for recovery-related flags.
- Emits KDTRACE start/done probes when compiled with hooks.
- Invokes `CLNT_CALL_MBUF` or `clnt_bck_call` for backchannel calls.
- Converts RPC-level failures to kernel errors and frees request mbufs on failure.
- Realigns reply mbufs, extracts NFS status, strips NFSv4 compound tag/op-count/sequence results, updates session slot sequence/window state, and detects op status.
- Retries `NFSERR_DELAY`, `NFSERR_GRACE`, and resource-style errors with exponential delay, with exceptions for non-idempotent/state-changing NFSv4 operations.
- Invalidates vnode/name caches on stale file-handle replies when possible.
- Marks `ND_INCRSEQID`, `ND_NOMOREDATA`, or `NFSERR_STALEDONTRECOVER` according to NFSv4 operation status.

## Notification and Signal Helpers
- `nfs_feedback` receives RPC reconnect/retransmit/OK callbacks and triggers `nfs_down`/`nfs_up`.
- `nfs_down`/`nfs_up` update mount state bits, emit VFS events (`VQ_NOTRESP`, `VQ_NOTRESPLOCK`), and print user-visible server status messages.
- `newnfs_sigintr` detects selected pending signals for `NFSMNT_INT` mounts and forced unmounts.

## Tunables
Defines sysctls for buffer packet scaling, reconnect count, NFSv3 jukebox delay, and weak-cache-consistency-on-error behavior.

## Dependencies
Depends on kernel RPC client APIs, GSS/Kerberos hooks, NFS mount/session structures, NFS request queues and locks, VFS events, signal APIs, mbuf XDR helpers, and DTrace probe arrays.

## Risks
- `newnfs_request` is highly stateful: changes can affect authentication lifetime, request mbuf ownership, NFSv4 slot leaks, seqid increments, retries, and stale-state recovery.
- Lazy connect and concurrent publication require careful `nr_mtx` discipline.
- Signal masking for interruptible mounts modifies thread signal state around sleeps/RPCs and must always restore it.
- Retry policy deliberately avoids replaying certain NFSv4 state-changing operations; broadening retries can break protocol correctness.
