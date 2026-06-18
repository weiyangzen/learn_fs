# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_print.c

Read completely: 1287 lines.

This file formats DNS resource records into zone-file-style presentation text. Public entry points are `ns_sprintrr` and `ns_sprintrrf`; private helpers include `prune_origin`, `charstr`, `addname`, `addlen`, `addstr`, and `addtab`.

The formatter handles many RR types explicitly: address/name records (`A`, `AAAA`, `NS`, `CNAME`, `PTR`, `DNAME`), structured records (`SOA`, `MX`, `AFSDB`, `RT`, `KX`, `PX`, `NAPTR`, `SRV`, `MINFO`, `RP`, `WKS`, `LOC`), DNSSEC/crypto-related records (`KEY`, `DNSKEY`, `SIG`, `RRSIG`, `DS`, `DLV`, `SSHFP`, `NSEC`, `NSEC3`, `NSEC3PARAM`, `DHCID`, `IPSECKEY`, `HIP`), and legacy/special records (`NSAP`, `A6`, `OPT`, `TKEY`, `TSIG`, `CERT`, `NXT`). Unknown or malformed records fall back to RFC3597-style hex output with an explanatory comment.

Important interactions: it relies on `ns_get16`, `ns_get32`, `dn_expand`, `ns_format_ttl`, `p_type`, `p_class`, `b64_ntop`, `inet_ntop`, and resolver name-canonicalization helpers. `prune_origin` and `addname` shorten names relative to an origin and emit `@`/`.` where appropriate.

Security/reliability notes: output writes go through `addstr`/`addlen` and report `ENOSPC` on short buffers. Several RR-specific branches do only minimal length checking before reading fields, especially older/incomplete formats such as `TKEY`, `TSIG`, `HIP`, and bitmap-based records; malformed RDATA is usually routed to `formerr`/hex output, but new RR parsers should add explicit `rdata < edata` guards before each field access.
