# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_mbuf.c

This file is the core NetBSD mbuf allocator and mbuf-chain manipulation implementation. It initializes `mb_cache` and the mbuf-cluster cache, maintains global mbuf sizing variables (`max_linkhdr`, `max_protohdr`, `max_hdr`, `max_datalen`), exposes `kern.mbuf` sysctls, tracks per-CPU mbuf type statistics, and optionally tracks mbuf ownership under `MBUFTRACE`.

`mbinit()` sets up pool caches, drain hooks, default and hard limits for clusters, low water marks, and optional owner accounting. `mb_drain()` asks protocol domains and network interfaces to release cached mbufs under memory pressure. Sysctl helpers expose immutable sizes, tunable `nmbclusters`/low-water values, computed `nmbclusters_limit`, statistics, and optional owner counters.

Allocation APIs include `m_get`, `m_gethdr`, `m_get_n`, `m_gethdr_n`, `m_clget`, and `m_getcl`. They initialize mbuf metadata, packet headers, receive-interface fields, checksum fields, packet attributes, and external cluster reference state. Free paths are `m_free`, `m_freem`, and `m_ext_free`; external storage may be embedded cluster storage, externally allocated storage, custom callback storage, or shared storage referenced through `m_ext_ref`.

The main chain operations are complete BSD mbuf primitives: append (`m_add`, `m_cat`), prepend (`m_prepend`), trim (`m_adj`), copy/shallow-copy/deep-copy (`m_copym`, `m_dup`, `m_copypacket`, `m_copydata`), contiguity repair (`m_ensure_contig`, `m_pullup`, `m_pulldown`, `m_copyup`), split (`m_split`), device-buffer import (`m_devget`), copyback and copy-on-write (`m_copyback`, `m_copyback_cow`, `m_makewritable`, `m_copyback_internal`), and defragmentation (`m_defrag`). Packet-header helpers copy, move, and remove `M_PKTHDR` metadata and tag chains.

The copy-on-write logic is the most delicate path: read-only external mbufs can be split, replaced with writable mbufs, optionally preserve original data, and maintain packet-header lengths. The external-reference macros and `m_ext_free()` rely on atomic refcounting and memory barriers to safely release shared clusters.

Debug and observability include DDB `m_print()`, diagnostic `m_verify_packet()`, per-CPU statistics, and optional owner claim/revoke accounting. Packet tags are managed with `m_tag_get/free/prepend/unlink/delete/delete_chain/find/copy/copy_chain`.

Key dependencies: pool cache, percpu, domain/protosw drain hooks, interface drain hooks, packet tag malloc type, mbuf macros from `sys/mbuf.h`. Risks are classic mbuf risks: packet length drift, shared external-storage lifetime, partial copyback failure, COW preserving invariants, packet-header/tag ownership, and paths that panic on impossible caller misuse.
