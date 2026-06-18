# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_socket.c

This file implements NFS socket transport, client RPC request/reply state handling, retransmission timers, and server socket receive dispatch. It is the central transport layer shared by NFS client and server code.

Client-side responsibilities:
- `nfs_connect()` creates/configures sockets, optionally binds reserved ports, connects stream sockets, enables keepalive/TCP options, reserves socket buffers, and initializes RTT/congestion fields.
- `nfs_disconnect()` and `nfs_safedisconnect()` close sockets, with receive-lock coordination in the safe variant.
- `nfs_send()` sends mbuf chains for client or server paths, handles datagram `ENOBUFS`, marks client requests for retransmit, and normalizes recoverable socket errors.
- `nfs_receive()` reads RPC replies from datagram or stream sockets, handles Sun RPC record marks for TCP, validates maximum packet size, reconnects reliable transports on errors, and realigns mbufs.
- `nfs_reply()` receives packets, matches replies by XID against outstanding requests, updates RTT/congestion state, handles duplicate/unexpected replies, and wakes or terminates requests.

RPC request state machine:
- `nfs_request()` drives states from setup through auth, transmit, wait, and process-reply.
- `nfs_request_setup()` allocates and initializes `nfsreq`, records the payload tail and async metadata, and rejects forced-unmount requests.
- `nfs_request_auth()` builds RPC headers with UNIX or Kerberos auth and prepends stream record marks when needed.
- `nfs_request_try()` queues the request, sends the first attempt, handles async races, and wakes reader helpers.
- `nfs_request_waitreply()` waits synchronously, unlinks completed requests, and wakes async writers when queue pressure drops.
- `nfs_request_processreply()` parses accepted/denied RPC replies, handles auth retry via `ENEEDAUTH`, NFSv3 `TRYLATER`, Kerberos nickname verifier saving, and final request cleanup.

Timer and cancellation:
- `nfs_timer_callout()` scans mounts for timed-out requests, drives retransmission logic, soft-terminates interrupted requests, and wakes server write-gather work.
- `nfs_timer_req()` computes RTT-derived timeouts, exponential backoff, retransmits datagram requests when allowed, and reports “not responding”.
- `nfs_nmcancelreqs()`, `nfs_softterm()`, and `nfs_hardterm()` terminate requests during forced unmount or completion.

Server-side responsibilities:
- `nfsrv3_procs[]` maps generic NFS procedure numbers to server handlers in `nfs_serv.c`.
- `nfs_rephead()` builds server RPC reply headers and embeds Kerberos verifier data when available.
- `nfs_getreq()` parses incoming RPC calls, validates RPC/NFS version and procedure, decodes UNIX or Kerberos auth, fills server credentials, and maps NFSv2 procedure numbers.
- `nfsrv_rcv_upcall()` and `nfsrv_rcv()` read incoming server socket data, queue complete records, and wake nfsd workers.
- `nfsrv_getstream()` extracts complete Sun RPC records from TCP stream fragments.
- `nfsrv_dorec()` turns queued records into `nfsrv_descript` objects.
- `nfsrv_wakenfsd()` assigns pending socket work to waiting nfsd threads.

Concurrency and locking:
- `nfs_sndlock()`/`nfs_sndunlock()` serialize reliable transport sends and reconnects.
- `nfs_rcvlock()`/`nfs_rcvunlock()` serialize receive-side access and avoid races where another thread receives a request’s reply.
- Async request completion moves requests from `nm_reqq` to `nm_reqrxq`.
- Server sockets use `nfssvc_sock` tokens and flags such as `SLP_GETSTREAM`, `SLP_DOREC`, and `SLP_DISCONN`.

Caveats:
- Kerberos crypto blocks remain incomplete/stubbed under `NFSKERB` conditionals.
- TCP stream handling is intentionally strict: impossible record lengths force disconnect/reconnect.
- `nfs_realign()` copies misaligned mbuf chains because RPC XDR parsing assumes 32-bit alignment.
