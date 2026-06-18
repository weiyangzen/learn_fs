# File Research: sources/os/bsd/openbsd-src/sys/sys/mbuf.h

Defines the mbuf packet-buffer ABI and kernel helper interface for OpenBSD networking.

Key contents:
- Mbuf sizing constants: `MSIZE`, `MLEN`, `MHLEN`, `MCLBYTES`, `MAXMCLBYTES`, `MINCLSIZE`.
- Core structures: `m_hdr`, `pkthdr`, `pkthdr_pf`, `mbuf_ext`, `mbuf`, `m_tag`, `mbuf_list`, `mbuf_queue`, and `mbstat`.
- Packet, external-storage, checksum, and type flags.
- Allocation and manipulation macros: `MGET`, `MGETHDR`, `MEXTADD`, `MCLGET`, `M_MOVE_PKTHDR`, `M_READONLY`, `M_PREPEND`.
- Packet tag IDs for IPsec, WireGuard, GRE, DLT, pf divert/reassembly, source route, tunnel, and CARP markers.

Key APIs:
- Allocation/free/copy/edit routines including `m_get`, `m_gethdr`, `m_clget`, `m_free`, `m_freem`, `m_copym`, `m_copyback`, `m_copydata`, `m_pullup`, `m_pulldown`, `m_prepend`, `m_split`, `m_defrag`.
- Tag routines `m_tag_get`, `m_tag_prepend`, `m_tag_delete`, `m_tag_find`, and copy helpers.
- Queue/list routines `ml_*` and `mq_*`.

Risk notes:
- Header movement and external-cluster reference macros encode ownership rules; misuse can leak tags, double-free clusters, or mutate shared read-only data.
