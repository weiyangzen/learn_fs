# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/convM2DNS.c

Parses DNS wire-format messages into internal `DNSmsg`/`RR` structures.

Key data:
- `Scan` tracks base/current/end pointers, error text, response code, stop flag, and truncation flag.

Primitive readers:
- `gchar`, `gshort`, `glong`.
- `gv4addr`, `gv6addr`.
- `gsym`, `gstr`, `gbytes`.
- `gname()` decodes domain names with compression pointers and detects pointer loops/bad labels.

RR parsing:
- `convM2RR()` reads resource records, allocates by type, decodes RDATA for supported types, ignores unknown types, and validates consumed RDLENGTH.
- `convM2Q()` parses questions.
- `rrloop()` builds linked RR lists for question, answer, nameserver, and additional sections.

Top-level:
- `convM2DNS(buf, len, m, codep)` parses header counts and sections, records format/truncation conditions, sets `Ftrunc` when needed, and returns an error string when recoverable errors occurred.

Robustness behavior:
- `errtoolong()` treats full-sized UDP payloads as likely truncated even if `Ftrunc` was not set.
- Handles EDNS extended-label byte by stopping parse rather than continuing.
- Detects reserved labels, bad compression pointers, and pointer loops.
- `mstypehack()` compensates for byte-swapped type fields seen from Windows 2000 PTR behavior by setting format response code.
- Allows some known malformed Windows/hints cases without noisy logging.
