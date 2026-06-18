# File Research: sources/os/plan9/9front/sys/src/9/ip/ipmux.c

Implements an IP packet filter/demultiplexer protocol.

Key elements:
- Parses filter expressions over version, protocol, source, destination, interface address, IP header bytes, and payload bytes.
- Builds canonical ordered filter chains and merges them into a decision tree.
- Supports masks and multiple values per comparison.
- Converts IPv6-style address filters to IPv4 offsets/widths where needed.
- Delivers matching packets to connected `ipmux` conversations, prepending the interface address.
- Sends unmatched packets to the normal protocol receiver.

Dependencies:
- Uses `Ip4hdr`, `Ip6hdr`, `Conv`, `Proto`, and queue primitives from the IP stack.
- Uses `Fsrcvpcol` to fall back to protocol dispatch.

Research notes:
- A missing `ver=` filter is expanded into both IPv6 and IPv4 branches.
- The tree stores refs so shared merged filter nodes can be removed safely on close.
- `ipmuxkick` expects user writes to be complete IP packets and injects them through IPv4 or IPv6 output.
