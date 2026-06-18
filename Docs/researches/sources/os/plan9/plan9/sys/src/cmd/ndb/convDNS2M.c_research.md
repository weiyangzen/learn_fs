# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/convDNS2M.c

Serializes internal `DNSmsg`/`RR` structures into DNS wire-format messages.

Key data:
- `Dict` stores up to 64 domain-name compression entries plus unpacked-name buffer and message start pointer.

Primitive packers:
- `psym`/`pstr` length-prefixed strings.
- `pbytes`, `puchar`, `pushort`, `pulong`.
- `pv4addr`, `pv6addr`.
- `pname()` with DNS label encoding and compression-pointer dictionary.

RR serialization:
- `convRR2M()` writes owner, type, class, TTL, RDLENGTH, and type-specific RDATA.
- Supports HINFO, CNAME, mailbox types, NS, MINFO, MX, A, AAAA, PTR, SOA, SRV, TXT, NULL, RP, KEY, SIG, CERT.
- `convQ2M()` writes DNS question owner/type/class.
- `rrloop()` serializes RR lists and counts successful entries.

Top-level:
- `convDNS2M()` zeroes output, serializes question/answer/ns/additional sections, sets truncation flag if packet overflows, then writes DNS header and returns encoded length.

Behavior notes:
- TTL is absolute in cache for non-db records, converted to relative by subtracting `now`.
- SRV target uses string packing, with comment noting RFC 2782 says no compression.
- If compression offset is too large for DNS packet format, logs an error.
