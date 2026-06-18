# File Research: sources/os/bsd/openbsd-src/sbin/iked/util.c

This file provides OpenIKED socket, address, formatting, mask, string, and debug-output utilities.

Key responsibilities:
- Address/port helpers:
  - `socket_af`, `socket_getport`, `socket_setport`, `socket_getaddr`
- Socket setup:
  - `socket_bypass` sets IPsec bypass levels so IKE UDP sockets are not themselves protected by IPsec.
  - `udp_bind` creates nonblocking UDP sockets, applies IPsec bypass, reuse options, destination-address receive options, and binds.
- Address comparison:
  - `sockaddr_cmp` compares IPv4/IPv6 sockaddr values with optional prefix masking.
- Ancillary-data I/O:
  - `sendtofrom` sends packets with explicit source address using `IP_SENDSRCADDR` or `IPV6_PKTINFO`.
  - `recvfromto` receives source and local destination address information from control messages.
- Formatting:
  - `print_spi`, `print_map`, `print_hex`, `print_hexval`, `print_hexbuf`, `print_bits`, `print_addr`, and `print_proto`.
- Mask conversion:
  - `mask2prefixlen`, `mask2prefixlen6`, `prefixlen2mask`, and `prefixlen2mask6`.
- String helpers:
  - `lc_idtype`, `get_string`, `expand_string`, and `string2unicode`.
- Debug output:
  - `print_debug` and `print_verbose`, gated by `log_getverbose`.

Security and correctness notes:
- Several print helpers use rotating static buffers sized by `IKED_CYCLE_BUFFERS`; callers must not retain pointers indefinitely.
- `recvfromto` preserves IPv6 link-local scope IDs from packet info.
- `mask2prefixlen6` fatals on non-contiguous IPv6 masks, enforcing canonical prefix masks.
- `string2unicode` is a simple zero-high-byte expansion and contains a byte-order caveat comment.
