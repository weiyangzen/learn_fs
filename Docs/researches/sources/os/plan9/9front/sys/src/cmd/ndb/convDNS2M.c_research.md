# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/convDNS2M.c

Packs internal DNS message/resource-record structures into DNS wire-format packets.

Key responsibilities:
- Maintains a small name-compression dictionary for packed domain names.
- Provides primitive packers for counted strings, symbols, raw bytes, unsigned integer fields, IPv4 addresses, IPv6 addresses, and compressed/uncompressed domain names.
- Enforces DNS label/domain/string size limits and output buffer bounds by returning beyond `ep` on overflow.
- `convRR2M` serializes resource records including HINFO, CNAME/MB/MD/MF/NS, MG/MR/MINFO, MX, A, AAAA, PTR, SOA, SRV, TXT, NULL, RP, DNSKEY/KEY, SIG, CERT, CAA, OPT, and unknown RDATA.
- Handles OPT records specially by writing UDP payload size and extended flags in the class/TTL fields.
- Computes RR TTL from db/expire/ttl state and clamps negative TTLs to zero.
- Serializes questions through `convQ2M`.
- `rrloop` packs sections and returns actual counts for questions, answers, authority, and additional records.
- `convDNS2M` writes section data first, accounts for optional EDNS record insertion, sets `Ftrunc` when output fills, then writes the DNS header with actual counts.

Important interactions:
- Depends on `dns.h` RR/DNSmsg layout and helper state such as `now`, `rrsupported`, and `dnslog`.
- Uses Plan 9 IP helpers `parseip` and `v6tov4`.

Notable quirks:
- The dictionary is limited to 64 entries but enough for normal DNS compression.
- SRV target names are intentionally packed without compression per RFC2782.
