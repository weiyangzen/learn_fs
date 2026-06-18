# File Research: sources/os/plan9/plan9/sys/src/9/ip/ip.h

Central header for the Plan 9 IP stack.

Key definitions:
- Core constants for address lengths, IPv4 offsets, protocol counts, channel counts, TTL/TOS defaults, IP versions, IPv4 header size, fragmentation flags, and route-tree sizing.
- Conversation states: `Idle`, `Announcing`, `Announced`, `Connecting`, `Connected`.
- IP stats enum matching counters emitted by `ipstats`.
- Fragment queue structures for IPv4 and IPv6 plus `Ipfrag` metadata layout.
- `IP` per-stack state: stats, fragment locks/free lists, fragment IDs, and routing flag.
- Wire `Ip4hdr`.
- `Conv` conversation object: addressing, ports, ownership, permissions, queues, listen queue, multicast bindings, protocol-private storage, and route cache.
- `Medium` media driver interface with bind/unbind/write, multicast, route propagation, address resolution, registration, prefix-to-address, and unbind policy hooks.
- `Iplifc`, `Iplink`, `Ipifc`, and `Ipmulti` for physical/logical interface and multicast bookkeeping.
- `Ipht` conversation hash-table declarations and match classes.
- `Proto` protocol registration callback table.
- `Fs` per-IP-stack container for protocols, ARP, self table, routes, log, IPv6 params, and ndb data.
- Router/host IPv6 parameter structures.
- Route tree, IPv4/IPv6 route payloads, and route type bits.
- `IPaux` channel auxiliary state used by devip and route tagging.
- ARP entry layout and public function prototypes across the stack.

Notable design:
- IPv4 is represented as IPv4-mapped 16-byte addresses throughout much of the stack.
- `Fs` contains several documented “kludge” pointers for `ipifc`, `ipmux`, and self-table access, reflecting tight coupling among stack modules.
