# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.c

`wire2str.c` implements sldns/libunbound DNS wire-format to presentation-format conversion. It defines lookup tables for DNSSEC algorithms, DS hashes, CERT algorithms, rcodes, opcodes, wire parse errors, EDNS flags/options, EDNS EDE codes, TSIG errors, and SVCB parameter keys.

The public allocation-returning helpers (`sldns_wire2str_pkt`, `sldns_wire2str_rr`, `sldns_wire2str_dname`, `sldns_wire2str_type`, `sldns_wire2str_class`, `sldns_wire2str_rcode`) are two-pass wrappers around buffer/scanner APIs: first compute required length, then allocate and print.

Packet scanning prints dig-style sections: header, question, answer, authority, additional, message size, and trailing garbage if present. RR scanning recognizes OPT records as EDNS, parses owner names with compression loop protection, prints TTL/class/type, reads rdatalen, then tries descriptor-driven pretty RDATA parsing before falling back to RFC3597-style `\# <len> <hex>` output. Malformed/partial data is usually rendered as an error plus available hex rather than aborting.

RDATA conversion is routed by `sldns_wire2str_rdf_scan()` across DNS field types: names, integers, periods, TSIG times, A/AAAA, character strings, APL, base32/base64/hex, NSEC bitmaps, NSEC3 salt/owner, CERT/algorithm fields, LOC, WKS/service bitmaps, NSAP, ATMA, IPSECKEY, HIP, ILNP64, EUI48/EUI64, unquoted/tag/long strings, SVCB parameters, and TSIG errors.

The file contains specialized SVCB/HTTPS SvcParam formatting for `mandatory`, `alpn`, `no-default-alpn`, `port`, `ipv4hint`, `ech`, `ipv6hint`, and default quoted values. It validates length constraints and returns failure to trigger unknown-format fallback when wire data is inconsistent.

EDNS handling prints OPT metadata, DO/CO flags, extended rcode, UDP size, and option comments. Supported option printers include LLQ, UL, NSID, DAU, DHU, N3U, client subnet, keepalive, padding, and EDE. Unknown options are hex-rendered.

Default RR comments are added for DNSKEY key tag/role/key size, RRSIG key tag, and NSEC3 opt-out. The implementation is careful about bounded output buffers, null termination through `sldns_str_print`, compressed-name loop limits, and preserving partial diagnostic output for corrupt DNS packets.
