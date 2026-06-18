# File Research: sources/os/bsd/openbsd-src/sbin/route/show.c

This file implements route table and preferred-source display for `route show` and `route sourceaddr`.

Key APIs:
- `get_sysctl()`: dynamically sizes and reads sysctl buffers, retrying on `ENOMEM`.
- `printsource()`: prints preferred IPv4 and IPv6 source addresses for a routing table.
- `p_rttables()`: dumps route entries via `NET_RT_DUMP`.
- `get_rtaddrs()`: splits packed sockaddr arrays into `RTAX_*` pointers.
- `p_rtentry()`: filters and prints one route entry, including MPLS and route labels.
- `p_sockaddr()`, `p_sockaddr_mpls()`, `p_flags()`: column formatting.
- `routename()`, `netname()`, `routename4()`, `routename6()`, `netname4()`, `netname6()`: numeric/name address formatting.
- `any_ntoa()`, `link_print()`, `mpls_op()`, `label_print()`: fallback, link-layer, MPLS, and route-label rendering.

Behavior and integration:
- Uses OpenBSD route sysctl data and route socket sockaddr packing conventions.
- Honors global `nflag`, `Fflag`, `verbose`, and `so_label`.
- Groups output by address family and prints family-specific headers for Internet, Internet6, Encap, MPLS, or unknown families.
- For IPv6, computes prefix length from netmask bytes and handles link-local scope compatibility code.

Risk notes:
- Formatting uses static buffers (`line`, `domain`) shared by address-name helpers, so returned strings are not reentrant.
- `p_rtentry()` assumes expected sockaddrs such as gateway exist for normal route entries.
- `netname6()` warns on illegal masks but continues by zeroing affected address bytes.
