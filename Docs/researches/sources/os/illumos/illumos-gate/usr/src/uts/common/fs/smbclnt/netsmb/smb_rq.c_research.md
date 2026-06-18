# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.c

## Purpose
Implements SMB request object lifecycle, SMB1 request header construction and reply parsing, simple request/reply execution, SMB1 transaction/transaction2/NT transaction packetization and multi-reply reassembly, and named-pipe transaction helper support.

## Key Elements
`smb_rq_alloc`, `smb_rq_init`, `smb_rq_new`, and `smb_rq_done` manage request objects, embedded request/reply chains, locks, CVs, and protocol-specific header reservations. Requests copy VC/share pointers from an existing held connection object but do not take their own VC holds; callers are responsible for holding the layer through device or mount ownership.

`smb_rq_fillhdr` rewrites the reserved SMB1 header with command, flags, UID, TID, PID, and MID just before send. `smb_rq_wstart/wend` and `smb_rq_bstart/bend` reserve and later fill SMB1 word-count and byte-count fields. `smb_rq_simple_timed` enqueues a normal SMB1 request, waits for a reply, and optionally retries only when the request is marked restartable and retry budget remains. `smb_rq_internal` is the IOD-thread/internal variant that bypasses reconnect logic and returns raw NT status.

`smb_rq_enqueue` handles SMB1 reconnect/tree-connect prerequisites, fills request UID/TID, and submits to the IOD. `smb_rq_reply` waits via the IOD, verifies SMB1 signing when required, parses the SMB header, maps DOS or NT status to errno, and treats `NT_STATUS_BUFFER_OVERFLOW` as nonfatal `SMBR_MOREDATA`. `smb_rq_parsehdr` also detects the special SMB1 negotiate request receiving an SMB2 response and returns `EPROTO` for the negotiate handler.

Transaction support includes `smb_t2_init/done/request`, `smb_nt_init/done/request`, `smb_t2_request_int`, `smb_nt_request_int`, `smb_t2_reply`, and `smb_nt_reply`. These routines fragment large parameter/data payloads across primary and secondary SMB1 transaction requests, use fixed alignment calculations and negotiated `vc_txmax`, collect multi-packet replies into separate parameter/data mdchains, and reject misordered parameter/data fragments. `smb_t2_xnp` wraps a named-pipe transaction and transfers ownership of input/output message chains.

## Dependencies
Depends on connection objects, IOD queueing/wait functions, SMB1 signing verification, SMB status mapping helpers, `mbchain`/`mdchain` and STREAMS mblk operations, SMB1 transaction constants, DTrace probes, and SMB2 negotiate parser hooks.

## Behavior/Risks
The request layer assumes the caller owns the lifetime of the VC/share, so invalid reference discipline outside this file can produce stale pointers. SMB is not safely restartable for most operations; `SMBMAXRESTARTS` is zero to avoid duplicating server-side effects. Multi-packet transaction code is offset/alignment sensitive and intentionally cannot handle misordered fragments despite the protocol allowing them. Operations that could leak server resources set no-interrupt flags in higher-level code so successful replies are not missed.
