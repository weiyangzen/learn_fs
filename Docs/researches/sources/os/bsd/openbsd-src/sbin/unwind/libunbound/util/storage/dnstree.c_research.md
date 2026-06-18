# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/dnstree.c

Implements DNS-oriented wrappers around the generic red-black tree for domain names and address/netblock lookup.

Name tree behavior:
- `name_tree_compare` sorts first by DNS class, then by `dname_lab_cmp`.
- `name_tree_insert` initializes a caller-owned node and inserts it.
- `name_tree_init_parents` walks ordered nodes and sets closest-encloser parent pointers using label-match counts.
- `name_tree_find` performs exact lookup.
- `name_tree_lookup` returns the closest enclosing configured name for a queried wire-format name/class.
- `name_tree_next_root` finds root-name entries by class, using recursive advancement to skip classes without root entries.

Address tree behavior:
- `addr_tree_compare` sorts by address, then netblock size.
- `addr_tree_addrport_compare` sorts using `sockaddr_cmp_scopeid`, effectively address/port/scope-oriented comparison.
- `addr_tree_insert` copies a socket address into the node and inserts it.
- `addr_tree_init_parents_node` and `addr_tree_init_parents` compute enclosing-subnet parent links by walking ordered nodes and using common-prefix lengths.
- `addr_tree_lookup` returns the closest enclosing netblock for a socket address.
- `addr_tree_find` performs exact netblock lookup.

Integration points:
- Depends on `util/data/dname.h` for DNS name comparison/root checks.
- Depends on `util/net_help.h` for sockaddr comparison, IP-family checks, and prefix matching.
- Used by TCP connection limit storage in this group.
