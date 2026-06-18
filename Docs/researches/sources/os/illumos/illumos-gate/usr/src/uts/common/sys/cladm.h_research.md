# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cladm.h

`cladm.h` defines private Sun Cluster administration syscall interfaces. Facilities include initialization and configuration; commands expose cluster boot flags, node id, highest node id, global device prefix, and cluster-controlled network addresses.

It defines boot flag bits, cluster network address structures for IPv4/IPv6 plus a 32-bit pointer form, and exports either kernel `cladmin`/`cluster_bootflags` or user `_cladm`.
