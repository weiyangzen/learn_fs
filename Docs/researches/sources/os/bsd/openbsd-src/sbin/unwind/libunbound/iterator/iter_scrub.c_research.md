# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.c

`iter_scrub.c` cleans parsed DNS replies before the iterator classifies and caches them. The public entry point `scrub_message()` verifies the QR bit and echoed question, clears AD/Z bits, then runs normalization followed by sanitization.

Normalization removes irrelevant answer data, enforces ordered CNAME chains, synthesizes CNAMEs from valid DNAME answers, limits excessive CNAME/DNAME chains, shortens oversized NS and RRSIG lists according to config, and marks justified A/AAAA additional-section glue. Authority-section CNAME/DNAME/A/AAAA records are stripped, unknown authority/additional types can be stripped under hardening, and promiscuous NS sets are removed in several answer/NODATA/NXDOMAIN cases.

Sanitization then removes extraneous answer RRsets, deletes out-of-zone data as potential poison, applies private-address filtering through `priv_rrset_bad()`, checks A/AAAA RR lengths and records EDE info for bad lengths, rejects overreaching NSEC records whose next-domain target leaves the server zone, and optionally stores certain potential poison or unverified glue into cache when hardening settings allow it.

Additional-section policy is conservative: A/AAAA glue is kept only if normalization marked it as directly referenced by relevant NS/MX/SRV-like data; if a referencing RRset is later removed, additional glue is removed as suspect. Hardened unverified-glue mode stores non-strict-subdomain glue separately with `PACKED_RRSET_UNVERIFIED_GLUE` and removes it from the response.

Special cases include transforming an authority-section DS RRset into the answer section for DS queries, retaining enough upward NS data to allow lame classification, and applying DNAME/CNAME TTL policy consistently when synthesizing a CNAME.
