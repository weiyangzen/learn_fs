# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.c

`str2wire.c` converts DNS presentation-format names, RRs, and individual RDATA fields into DNS wire format. It returns structured parse errors that combine an error code with an input offset.

Domain-name parsing builds uncompressed wire-format names, handles escaped octets/literals, validates label/domain limits, detects relative names, and appends an origin when requested. `@` and empty owner handling use origin, previous owner, or root fallback depending on parse context.

The RR parser reads owner, optional TTL, optional class, and type, then writes the wire RR header. RDATA parsing is driven by the descriptor table from `rrdef.c`; it handles per-field delimiters, quoted strings, parenthesized multiline input, variable field counts, HIP and length-prefixed data special cases, and RFC3597 `\# <length> <hex>` unknown-RR syntax. It writes RDLENGTH after parsing.

SVCB/HTTPS receive substantial special handling. The parser recognizes named and numeric SvcParamKeys, encodes mandatory/alpn/no-default-alpn/port/ipv4hint/ech/echconfig/ipv6hint/dohpath and generic key values, supports quoted/unescaped values, sorts SvcParams by numeric key, and optionally compiles semantic checks for duplicates and mandatory constraints.

`fp2wire_rr_buf()` reads one logical zone-file RR through the tokenizer, handles `$ORIGIN`, `$TTL`, `$INCLUDE`, other directives, previous-owner state, line numbers, and default TTL updates. There are also safe raw-wire accessors for type, class, TTL, RDLENGTH, and RDATA pointers.

The RDF converters cover integers, IPv4/IPv6 addresses, character strings, APL, base64/base32hex, hex, NSEC bitmaps, RR type/class names, CERT algorithms, DNSSEC algorithms, TSIG errors, DNSSEC times, TSIG 48-bit times, periods, LOC, WKS service bitmaps, NSAP, ATMA, IPSECKEY, NSEC3 salt, ILNP64, EUI48/EUI64, CAA tags, long strings, HIP, and 16-bit-length-prefixed data.

The file is tightly coupled to `parse.c`, `parseutil.c`, `rrdef.c`, `wire2str` lookup tables, and `sbuffer`. It is the main ingestion path for zone-file text, resolver hints, local data, and any configuration that supplies DNS RRs in presentation form.
