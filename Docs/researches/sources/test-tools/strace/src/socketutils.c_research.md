# sources/test-tools/strace/src/socketutils.c

Purpose: runtime socket metadata resolver, mapping socket inodes to printable protocol/address details and discovering generic netlink family names.

Important APIs/types/functions: cache helpers, `send_query`, `receive_responses`, `inet_send_query`, `inet_parse_response`, `unix_send_query`, `unix_parse_response`, `netlink_send_query`, `netlink_parse_response`, `get_proto_by_name`, `get_family_by_proto`, `get_sockaddr_by_inode`, and `genl_families_xlat`.

Control flow: socket inode lookup first checks a 1024-slot direct-mapped cache. On miss it opens a NETLINK_SOCK_DIAG socket, queries either a known protocol or all protocols, parses matching inet/unix/netlink diagnostic responses, caches a formatted string, and falls back to `PROTO:[inode]` when only a protocol name is known. Generic netlink discovery lazily opens NETLINK_GENERIC, dumps controller families, and builds a dynamic xlat table from family id/name attributes.

State and persistence behavior: global inode cache stores allocated detail strings and replaces entries by `inode & CACHE_MASK`. A static fallback string and static dynamic xlat persist across calls. Cache entries are process-local and never invalidated except by collision replacement.

Dependencies and integration points: depends on netlink diag UAPI, protocol xlat tables, `getfdproto`, kernel version (`os_release`) for UNIX dump behavior, `dyxlat`, and low-level socket syscalls from the tracer process.

Risks: runtime diagnostic sockets can fail due to permissions, kernel support, namespaces, or races with socket closure. Direct-mapped cache can return stale details if an inode is reused before collision replacement. Generic netlink family dump assumes controller response version 2.

Test signals: inode lookup for TCP/UDP IPv4/IPv6, UNIX path and peer info, netlink protocol info, unknown protocol fallback, cache hit/collision, failed diagnostic socket, older UNIX diag dump flag behavior, and generic netlink family xlat creation.
