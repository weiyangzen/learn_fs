# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.c

Implements minimal PROXY protocol v2 helpers used by `netevent.c`. It stores caller-supplied endian-writing callbacks in a global `proxy_protocol_data` via `pp_init()`, so header generation can use the project's normal wire-format writers.

`pp_lookup_error()` maps parse error enum values to short static messages used in network error logs. The lookup table covers no error, undersized input, signature/version mismatch, unknown command, and unknown family/protocol.

`pp2_write_to_buf()` writes a PROXYv2 header for an IPv4 or IPv6 source address. It checks source presence and output capacity, emits the fixed signature, version/PROXY command, family/protocol based on stream versus datagram, address block length, source address, zero destination address, source port, and destination port field. It returns the total header size on success or `0` for unsupported families or insufficient space. AF_UNIX is not emitted.

`pp2_read_header()` validates an existing PROXYv2 header without interpreting all address data. It checks minimum header size, signature, version, full declared length availability, supported LOCAL/PROXY command, and supported UNSPEC, IPv4, IPv6, or UNIX family/protocol combinations. It returns `PP_PARSE_NOERROR` on success or a specific parse error code.
