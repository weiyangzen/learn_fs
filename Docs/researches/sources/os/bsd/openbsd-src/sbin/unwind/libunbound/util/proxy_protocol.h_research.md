# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.h

Defines the PROXY protocol v2 constants, wire layout, parse errors, and helper prototypes. The file explicitly supports only PROXYv2 and notes that TLVs are not currently supported.

Constants cover the 16-byte minimum header size, 12-byte v2 signature, and protocol version value. Enums define v2 commands (`LOCAL`, `PROXY`), address families (`UNSPEC`, `INET`, `INET6`, `UNIX`), transport protocols (`UNSPEC`, `STREAM`, `DGRAM`), and the accepted family/protocol byte combinations.

`struct pp2_header` models the fixed PROXYv2 header plus a union of address payloads: IPv4 address/port pair with 12-byte payload, IPv6 address/port pair with 36-byte payload, and AF_UNIX source/destination paths with 216-byte payload.

`enum pp_parse_errors` defines the parse result contract returned by `pp2_read_header()`: success, insufficient size, wrong v2 header, unknown command, or unknown family/protocol.

The declared API initializes endian writers (`pp_init()`), returns parse error text (`pp_lookup_error()`), writes a PROXYv2 header for IPv4/IPv6 source addresses (`pp2_write_to_buf()`), and validates a PROXYv2 header from a buffer (`pp2_read_header()`).
