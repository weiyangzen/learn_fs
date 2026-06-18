# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.h

`str2wire.h` declares the text-to-wire DNS conversion API. It defines IPv4/IPv6 address lengths, the 64 KiB RR buffer recommendation, default TTL, SVCB key constants, SVCB parameter limits, and the parse-error code namespace.

The public API converts domain names, full RRs, question-only RRs, file-stream RRs, and individual RDF values into wire format. Full RR output layout is explicitly documented as uncompressed owner name followed by type, class, TTL, RDLENGTH, and RDATA; helper accessors retrieve those fields safely despite possible unaligned storage.

`struct sldns_file_parse_state` stores `$ORIGIN`, previous owner name, current default TTL, and line number across zone-file reads. `sldns_fp2wire_rr_buf()` uses this state to honor zone-file directives and owner-name inheritance.

The header exposes converters for every RDF type implemented in `str2wire.c`, including specialized DNSSEC, LOC, WKS, IPSECKEY, NSEC3, ILNP/EUI, CAA, HIP, and length-prefixed data formats. It also declares `sldns_get_errorstr_parse()` and whitespace stripping for callers that need diagnostics or directive handling.
