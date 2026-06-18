# File Research: sources/os/bsd/freebsd-src/sys/sys/mbuf.h

Defines FreeBSD mbuf packet-buffer structures, flags, external storage model, packet tags, allocation/free APIs, queue helpers, and mchain helpers.

Key content:
- Defines mbuf sizing macros `MHSIZE`, `MPKTHSIZE`, `MLEN`, `MHLEN`, `MINCLSIZE`, and `M_NODOM`.
- Kernel SDT probes cover mbuf init, allocation, cluster attachment, free, and chain free.
- `struct m_tag` represents packet annotations with cookie/id/length/free callback.
- `struct m_snd_tag` tracks interface send tags with refcount and operations table.
- `struct pkthdr` stores per-packet metadata: receive/send interface union, leaf receive interface, tags, total length, flow id, checksum/offload flags, FIB, NUMA domain, RSS hash type, timestamps/header lengths, persistent and local scratch storage.
- `struct m_ext` describes external storage or multi-page unmapped storage, including embedded or external refcounts, storage size/type/flags, buffer/page vectors, TLS header/trailer space, free callback, and args.
- `struct mbuf` combines chain pointers, data pointer, length, type/flags, optional packet header, external storage, multi-page TLS metadata, and inline data.
- Defines extensive mbuf flags: external storage, packet header, end-of-record, readonly, broadcast/multicast/promisc, VLAN tag, unmapped ext pages, timestamps, and protocol-specific flags.
- Defines RSS hash types, external storage types, external flags, checksum/offload flags, compatibility aliases, and mbuf content types.
- Declares UMA zones and large API surface for mbuf manipulation: adjust, append, copy, collapse, defrag, demote, external add, fragment, free, get variants, length, pullup/pulldown, split, uiomove, unshare, send tag, rcvif serialization, and unmapped conversions.
- Inline helpers handle page length sanity, type/zone selection, raw/initialized allocation, cluster setting, protocol-flag clearing, last mbuf lookup, refcount lookup, writability checks, assertions, start/size/leading/trailing space, prepend, receive interface access, packet tag operations, send tag ref/release, and single-mbuf free.
- Packet tag IDs include IPsec, bridge, gif/gre, checksum, encapsulation, IPv6, dummynet, divert, MAC label, PF, CARP, NAT-T, ND, OpenVPN, and more.
- `struct mbufq` implements packet queues with max length and inline enqueue/dequeue/flush/drain/concat helpers.
- `struct mchain` tracks chains by `m_stailq`, with logical data length and memory-consumption accounting plus get/split/uiomove APIs.
- Timestamp helpers convert packet timestamps to `timespec` or `timeval`.
- Debugnet and TLS-session helper declarations are present.

Research relevance:
- This is the core network I/O buffer ABI. It intersects with filesystem/storage through sendfile, unmapped pages, UIO conversion, KTLS, mbuf-backed memory descriptors, MAC labels, and kernel I/O paths.
- `memdesc.h` can construct mbuf chains from abstract memory descriptors and uses `M_EXT`/`M_EXTPG` semantics.
- `mchain.h` provides protocol serialization/deserialization helpers on top of mbufs.

Cautions:
- Many structure sizes and offsets are asserted in implementation files; layout changes are dangerous.
- `M_WRITABLE()` is conservative and responsibility still rests with callers.
- `m_cljset()` is explicitly described as dangerous because it cannot prove the cluster is new/unreferenced.
- `m_free()` may release packet tags, send tags, external storage, ext pages, or the UMA mbuf depending on flags.
