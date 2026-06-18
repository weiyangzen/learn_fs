# File Research: sources/os/bsd/dragonflybsd/sys/sys/mchain.h

Kernel-only helper API for encoding and decoding typed values into/from mbuf chains. Defines copy modes, custom copy callback type, `mbchain` write builder, and `mdchain` read cursor.

APIs initialize, finalize, detach, reserve, fix headers, append integers in big/little endian, append memory/mbufs/uio, and extract typed values/memory/mbufs/uio. Relevant to network filesystems and protocols that serialize filesystem messages over mbufs.
