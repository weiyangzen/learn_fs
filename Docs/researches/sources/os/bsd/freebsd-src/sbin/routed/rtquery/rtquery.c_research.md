# File Research: sources/os/bsd/freebsd-src/sbin/routed/rtquery/rtquery.c

Standalone RIP query and trace-control utility for probing `routed` instances and printing RIP responses.

Key responsibilities:
- Parses options for numeric output, gated-style poll requests, RIPv1 mode, wait timeout, specific target route, trace commands, and cleartext/MD5 authentication.
- Builds RIP request, poll, trace-on, trace-off, and trace-dump packets.
- Sends queries to one or more hosts on the RIP UDP port and waits for distinct responders.
- Supports full-table requests or single-route requests with host/network/prefix parsing.
- Emits RIPv2 cleartext or MD5 authentication records in outgoing requests.
- Prints response source names/addresses, packet version/size, route destination, mask/prefix, metric, name, next-hop, tag, and authentication contents.
- Verifies displayed MD5 response trailers against the supplied password.
- Provides local helpers for printable secret strings, classful mask guessing, network parsing, and escaped password parsing.

Dependencies:
- Uses `<protocols/routed.h>`, UDP sockets, resolver APIs, MD5 functions from `libmd` or NetBSD `<md5.h>`, and RIP packet constants shared with routed.

Notable risks:
- Trace commands require UID 0 and bind to a reserved UDP port, matching daemon-side trust checks.
- MD5 query generation uses packet-length-sensitive trailer construction; incorrect length math breaks authentication.
- Response display is diagnostic, not strict validation; it reports malformed lengths, unusual masks, and auth records while continuing to parse what it can.
