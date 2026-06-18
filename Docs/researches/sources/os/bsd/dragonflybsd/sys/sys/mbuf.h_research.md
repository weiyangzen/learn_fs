# File Research: sources/os/bsd/dragonflybsd/sys/sys/mbuf.h

Defines DragonFly mbuf packet buffer layout, flags, allocation macros, packet headers, external storage descriptors, packet tags, checksum flags, firewall/PF metadata, allocator statistics, manipulation routines, and mbuf queue helpers.

Core structures include `m_hdr`, `pkthdr_pf`, `m_tag`, `pkthdr`, `m_ext`, `mbuf`, `mbstat`, and `mbufq`. Kernel APIs cover allocation, free, append, copy, pullup/pulldown, split, defrag, external buffer attach, packet header movement, tag management, and queue operations. Filesystem relevance is indirect through network filesystems, sockets, sendfile, and kernel I/O paths that pass data through mbufs.
