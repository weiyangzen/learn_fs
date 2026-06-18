# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_sockbuf.c

## Purpose
Implements FreeBSD socket buffer primitives: mbuf accounting, readiness tracking, wakeups, buffer reservation, append/compress helpers, record/address/control insertion, front-drop/cut operations, send-pointer helpers, and exported socket-buffer status. It is the common low-level machinery used by socket receive and send paths.

## Main Elements
- Global tuning: `sb_max`, `sb_max_adj`, `sb_efficiency`, and sysctls for maximum socket buffer size and mbuf waste factor.
- Accounting helpers: `sballoc()`, `sbfree()`, and KTLS-specific `sballoc_ktls_rx()` / `sbfree_ktls_rx()` update byte counts, mbuf memory counts, control bytes, ready bytes, first-not-ready pointer, TLS counts, and send pointer cache.
- Readiness model: `sbready()` marks `M_NOTREADY` mbufs or ext-page subranges ready, advances `sb_acc` only when the first blocking mbuf becomes ready, and calls `sbready_compress()` to coalesce newly ready data.
- Wakeups and half-close: `socantsendmore*()`, `socantrcvmore*()`, `soroverflow*()`, `sbwait()`, `sowakeup()`, `sorwakeup_locked()`, and `sowwakeup_locked()` integrate select, kqueue, upcalls, AIO, SIGIO, socket splicing, and KTLS receive checks.
- Buffer reservation: `soreserve()`, `sbreserve_locked_limit()`, `sbreserve_locked()`, `sbunreserve_locked()`, `sbsetopt()`, `sbrelease*()`, and `sbdestroy()` enforce `RLIMIT_SBSIZE`, high/low water marks, autosize flags, and reserved mbuf budget.
- Append paths: `sbappend_locked()`, `sbappend()`, `sbappendstream_locked()`, `sbappendstream()`, `sbappendrecord_locked()`, `sbappendrecord()`, `sbappendaddr*()`, and `sbappendcontrol*()` maintain record chains with `m_nextpkt` and mbuf chains with `m_next`.
- Compression: `sbcompress()` drops empty mbufs, coalesces small writable mbufs where safe, handles `M_EOR`, preserves record and tail invariants, and avoids coalescing not-ready/TLS-session data. `sbcompress_ktls_rx()` appends encrypted TLS RX data to the separate TLS chain.
- Debug invariants: optional `sblastrecordchk()`, `sblastmbufchk()`, and `sbcheck()` validate `sb_lastrecord`, `sb_mbtail`, accounting totals, not-ready placement, and TLS detached data counts.
- Drop/cut helpers: `sbflush*()`, `sbcut_internal()`, `sbdrop*()`, `sbcut_locked()`, and `sbdroprecord*()` remove bytes or records while preserving accounting and special handling for externally referenced not-ready mbufs.
- Send helpers and ancillary data: `sbsndptr_noadv()`, `sbsndptr_adv()`, `sbsndmbuf()`, `sbcreatecontrol()`, and `sbtoxsockbuf()`.

## Dependencies And Integration
Depends on mbuf internals, socket locks, select/kqueue, AIO callback integration, KTLS when enabled, resource accounting, socket upcalls, socket splice dispatch, sysctls, and protocol-level send/receive assumptions. The file is a shared substrate for stream and record-oriented protocols.

## Risk Notes
The central invariant is that `sb_mb`/`sb_lastrecord` describe records while `sb_mbtail` describes the final mbuf in the final record; many helpers panic under debug if this drifts. `M_NOTREADY` complicates accounting because `sb_ccc` includes queued bytes but `sb_acc` only includes visible ready bytes. `sbcut_internal()` must not free externally referenced not-ready mbufs and has special paths for KTLS detached/decryption queues. Wakeup functions intentionally unlock the sockbuf and may call into other subsystems, so callers rely on the documented lock-release behavior.
