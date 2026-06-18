# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.h

`rrdef.h` declares DNS RR constants, enums, and descriptor APIs. It defines maximum label/domain sizes, RR overhead, DNSSEC key flag bits, RDF byte-size constants, NSEC/APL constants, and the externally visible RR class lookup table.

The RR type enum includes standard types, DNSSEC, modern service and security types, query pseudo-types, and the full 0-65535 range bounds. The RDF type enum describes how individual RDATA fields are parsed and formatted: domain names, integers, addresses, strings, base encodings, NSEC bitmaps, algorithms, time/period values, TSIG fields, LOC/WKS/NSAP/ATMA/IPSECKEY, NSEC3 components, ILNP/EUI values, CAA tags, long strings, and SVCB parameters.

The header also defines DNSSEC algorithm IDs, DS hash IDs, CERT algorithm IDs, EDNS option codes, EDE codes, TSIG/TKEY extended errors, and BADCOOKIE.

`struct sldns_rr_descriptor` is the central schema record for a type: type code, name, min/max fields, wireformat RDF list, variable RDF type, compression policy, and DNAME count. The declared functions expose descriptor lookup and name-to-type/class conversion.
