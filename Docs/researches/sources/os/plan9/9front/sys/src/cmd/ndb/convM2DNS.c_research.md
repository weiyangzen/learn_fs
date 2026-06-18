# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/convM2DNS.c

Parses DNS wire-format packets into internal `DNSmsg` and `RR` structures.

Key responsibilities:
- Uses a `Scan` cursor to track packet bounds, current position, parsing errors, outgoing response code, stop/truncation flags, and formatted diagnostics.
- Provides safe readers for bytes, shorts, longs, IPv4/IPv6 addresses, DNS strings, raw byte sequences, and compressed domain names.
- Implements DNS name decompression with pointer-loop limits and EDNS/reserved-label detection.
- Converts wire RRs to internal records for HINFO, CNAME/MB/MD/MF/NS, MG/MR/MINFO, MX, A, AAAA, PTR, SOA, SRV, TXT, NULL, RP, DNSKEY/KEY, SIG, CERT, CAA, OPT, and unknown RDATA.
- Converts questions separately with owner/type/class.
- Includes a Windows 2000 type-field byte-order workaround that can set format-error response feedback.
- Handles bad lengths defensively, including special tolerance for malformed hints and a known malformed CNAME reverse-lookup pattern.
- Builds section lists for questions, answers, nameservers, and additional records.
- Returns a duplicated error string for answer/nameserver parse errors while still attempting to parse additional records.

Important interactions:
- Allocates DNS structures through `rralloc`, `dnlookup`, `emalloc`, and related helpers from the DNS subsystem.
- `codep` receives a response code such as `Rformat` when parsing should abort with an immediate reply.

Notable quirks:
- If input appears truncated without the truncation flag, it may set `Ftrunc` heuristically.
- EDNS extended labels set a stop flag and are treated like a graceful parser stop.
