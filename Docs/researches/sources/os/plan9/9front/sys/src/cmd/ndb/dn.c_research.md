# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dn.c

Implements the DNS domain-name and resource-record cache core for `ndb/dns`.

Key elements:
- Maintains a hash table of `DN` objects keyed by case-insensitive domain name plus class.
- Provides global time state via `timems`, and installs DNS-specific formatters in `dninit`.
- Implements `dnlookup`, `idnlookup`, and `ipalookup` for canonical DNS object allocation.
- Implements RR cache insertion, duplicate removal, TTL/expiry handling, and positive/negative RR replacement.
- Uses a two-mark activity/GC scheme: `getactivity` and `putactivity` track active request marks, while `dnageall` ages expired RRs and sweeps unreferenced `DN`s only when safe.
- Handles authoritative database conversion rules in `dnauthdb`, including minimum SOA TTL enforcement and anti-spoofing for local areas.
- Provides RR list helpers: `rrlookup`, `rrcopy`, `rrcat`, `rrremneg`, `rrremtype`, `rrremowner`, `unique`, and `randomize`.
- Provides text and RR formatters `%R`, `%Q`, and `%\`, including escaping for TXT data.
- Allocates/frees type-specific RR payloads in `rralloc` and `rrfree`.
- Generates reverse PTR records with `dnptr`.

Notable behavior:
- Database RRs get an effective attach TTL of one year; short network TTLs are extended to at least ten minutes to keep answers usable during a request.
- `rrlookup` prioritizes authoritative database data, then fresh authoritative network data, then fresh unauthoritative network data, then unauthoritative database hints.
- Negative cached records are first-class `RR`s with `negative`, `negsoaowner`, and `negrcode`.
- `slave` forks request worker processes with shared memory and returns the parent to the main loop via `longjmp`.

Risks and quirks:
- `certequiv` compares fields to themselves (`a->type == a->type`, etc.), which appears to ignore the `b` certificate fields except for the block comparison.
- The GC logic depends on correct `getactivity`/`putactivity` pairing across forked request workers.
- `rrfree` asserts the RR is not cached, so all cache unlink paths must clear `cached` first.
