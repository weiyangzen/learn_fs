# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mbuf.c

Read completely: 1815 lines.

## Purpose
Implements FreeBSD mbuf and mbuf-cluster allocation, packet mbuf zones, jumbo clusters, external storage reference cleanup, unmapped external-page mbufs, send tags, receive-interface serialization, and debugnet emergency mbuf pools.

## Main Elements
- Tunables and sysctls manage `nmbufs`, `nmbclusters`, jumbo cluster limits, `maxmbufmem`, `mb_use_ext_pgs`, and active send-tag count.
- `mbuf_init()` creates UMA zones for mbufs, 2K clusters, packet mbufs, page-size jumbo clusters, 9K jumbo clusters, and 16K jumbo clusters.
- Constructors/destructors `mb_ctor_mbuf()`, `mb_ctor_clust()`, `mb_ctor_pack()`, `mb_dtor_mbuf()`, and `mb_dtor_pack()` initialize normal, cluster-backed, and packet-zone mbufs.
- `mb_zinit_pack()` and `mb_zfini_pack()` attach/release packet-zone clusters when objects move between UMA cache and backing keg.
- `m_clget()`, `m_cljget()`, `m_get2()`, `m_get3()`, `m_getjcl()`, `mc_get()`, and `m_getm2()` allocate mbufs and chains sized to caller needs.
- `m_extadd()` attaches caller-provided external storage.
- `m_freem()`, `m_freemp()`, `m_free_raw()`, `mb_free_ext()`, and `mb_free_extpg()` release chains and external backing storage based on `ext_type`.
- `mb_alloc_ext_pgs()`, `mb_alloc_ext_plus_pages()`, `mb_mapped_to_unmapped()`, `mb_unmapped_compress()`, and `mb_unmapped_to_ext()` handle unmapped page-backed mbufs for sendfile/TLS paths and fallback conversion.
- Debugnet support builds preallocated mbuf/cluster cache zones and temporarily swaps global zone pointers during panic-time network I/O.
- `m_snd_tag_*()` wraps interface send-tag lifecycle and accounting.
- `m_rcvif_serialize()` and `m_rcvif_restore()` preserve receive-interface identity across deferred processing.

## Dependencies And Integration
Uses UMA, VM pages, direct-map support, sf_bufs, KTLS, network `ifnet`, NET_EPOCH, eventhandlers, sysctl, counters, debugnet, and mbuf macros from `sys/mbuf.h`. It is core networking infrastructure but also supports kernel I/O paths that need packet buffers, TLS/sendfile page references, and panic-time network dump/debug flows.

## Risk Notes
Reference counting for external storage is subtle: embedded and shared refcounts, `M_NOFREE`, packet-zone special handling, and TLS deferred freeing all have different paths. Unmapped mbufs cannot always be converted, especially TLS mbufs. Debugnet overwrites global zone pointers and relies on careful start/finish pairing. Sysctl limit increases are allowed but shrinking is rejected.
