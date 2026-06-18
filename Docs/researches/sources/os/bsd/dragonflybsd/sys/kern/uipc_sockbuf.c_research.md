# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_sockbuf.c

## Role

This file implements low-level `struct sockbuf` mbuf queue manipulation. It is the record/data queue layer used by `struct signalsockbuf` in sockets, and it is responsible for preserving socket-buffer byte counts, mbuf accounting, record boundaries, end-of-record flags, and ancillary-data layout.

It does not implement sleeping, readiness notification, or socket state. Those live in `uipc_socket.c` and `uipc_socket2.c`; this file only mutates the mbuf chains and accounting fields.

## Major Responsibilities

- Append ordinary data to the current record with `sbappend()`.
- Append stream data with `sbappendstream()`, an optimized path for protocols such as TCP that maintain a single non-atomic record and do not carry control data.
- Append a new record with `sbappendrecord()`.
- Append source address, optional control data, and payload with `sbappendaddr()`.
- Append control data followed by payload with `sbappendcontrol()`.
- Coalesce or link mbufs into a sockbuf with `sbcompress()`.
- Flush all mbufs from a buffer with `sbflush()`.
- Drop bytes or whole records from the front with `sbdrop()` and `sbdroprecord()`.
- Remove the leading mbuf and update record pointers with `sbunlinkmbuf()`.
- Build `MT_CONTROL` ancillary-data mbufs with `sbcreatecontrol()`.

## Queue Model

The sockbuf is a list of records. Mbufs inside one record are linked through `m_next`; records are linked through `m_nextpkt`. `sb_mb` points to the first mbuf, `sb_lastrecord` points to the first mbuf of the final record, and `sb_lastmbuf` points to the final mbuf in the final record.

The file carefully maintains three classes of state:

- `sb_cc`: queued payload/control/address bytes.
- `sb_mbcnt`: mbuf storage charged to the buffer.
- `sb_lastrecord` and `sb_lastmbuf`: hints required for fast append and correct record traversal.

When `SOCKBUF_DEBUG` is enabled, `_sbcheck()` recomputes length and mbuf counts and validates `sb_lastrecord`/`sb_lastmbuf` consistency.

## Append Behavior

`sbappend()` appends to the last record unless the last record or last mbuf has `M_EOR`, in which case it starts a new record through `sbappendrecord()`. It then delegates actual packing to `sbcompress()`.

`sbappendstream()` asserts that the incoming mbuf chain has no `m_nextpkt` chain and directly calls `sbcompress()`. A protocol using this path must use it exclusively because it assumes stream-style single-record layout.

`sbappendrecord()` splits the first mbuf from the incoming chain, inserts it as the first mbuf of a new record, accounts for that first mbuf, propagates `M_EOR` from the first mbuf to the second mbuf when needed, and compresses the remaining chain after the first mbuf.

`sbappendaddr()` prepends an `MT_SONAME` mbuf containing a sockaddr, concatenates control and payload data behind it, accounts every mbuf, inserts the result as a new record, and moves `M_EOR` to the final mbuf. It rejects addresses larger than `MLEN`.

`sbappendcontrol()` requires non-null control and payload mbufs. It counts both chains, concatenates payload behind control, inserts the chain as a new record, moves `M_EOR` to the final payload mbuf, and updates byte and mbuf counts in bulk.

## Compression And Freeing

`sbcompress()` is the central insertion routine. It discards empty mbufs when safe, coalesces small writable mbufs into the prior mbuf when possible, links remaining mbufs, updates accounting, clears intermediate `M_EOR`, and finally propagates any observed `M_EOR` to the last inserted mbuf.

Freeing is deliberately deferred through a local `free_chain`. This avoids calling `m_free()` in the middle of a partially updated sockbuf state, because freeing may block or otherwise break the atomicity assumptions of the buffer mutation.

The coalescing path avoids merging into an `M_EOR` mbuf or an `M_SOLOCKED` mbuf. The `M_SOLOCKED` guard matters for the TCP receive fast path in `uipc_socket.c`, where mbufs can be temporarily locked while userland copyout proceeds without holding the receive token.

## Drop And Flush Behavior

`sbdrop()` removes bytes from the front of the sockbuf. It can trim a leading mbuf in place or unlink whole mbufs through `sbunlinkmbuf()`. If a record is exhausted but more bytes must be dropped, it continues into the next record. It also removes zero-length mbufs left at the front of the current record.

`sbdroprecord()` removes the entire first record, updates first-record and last hints, frees the record chain, and rechecks invariants.

`sbflush()` repeatedly drops all queued bytes until mbuf accounting reaches zero, then asserts that byte count, mbuf list, mbuf accounting, and last-mbuf hint are all clear. It detects impossible states where `sb_cc` is zero but a non-empty leading mbuf remains.

`sbunlinkmbuf()` only supports unlinking the current head mbuf. It updates `sb_mb`, moves `m_nextpkt` to the next mbuf when a record still has data, clears final-record hints on empty buffers, and optionally chains the removed mbuf onto a deferred free list.

## Ancillary Data

`sbcreatecontrol()` allocates an `MT_CONTROL` mbuf large enough for a `cmsghdr` plus aligned payload. It rejects control payloads whose `CMSG_SPACE(size)` exceeds `MCLBYTES`, fills `cmsg_len`, `cmsg_level`, and `cmsg_type`, and optionally copies caller data into `CMSG_DATA()`.

## Notable Assumptions And Risks

- Most callers are expected to hold the appropriate socket-buffer token or otherwise serialize access. This file validates structure but does not acquire higher-level locks.
- `sbappendcontrol()` asserts that both control and payload are present; it is not a generic nullable ancillary-data append helper.
- `sbunlinkmbuf()` assumes the mbuf being removed is exactly `sb_mb`.
- `M_EOR` propagation is intentionally centralized so record-boundary semantics survive empty-mbuf removal and coalescing.
- Deferred frees are important for correctness; moving `m_free()` calls into the middle of mutation paths would risk exposing inconsistent sockbuf state.
