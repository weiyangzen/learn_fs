# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dns.c

`snoopy` DNS decoder using Plan 9 NDB DNS conversion routines.

Key behavior:
- Calls `convM2DNS()` to parse DNS wire messages into `DNSmsg`.
- Formats DNS id/flags, then exposes pseudo-protocol stages for question, answer, authority, and additional records.
- `fmtrr()` prints RR owner/type/TTL and type-specific data for common RR types.
- Supplies local implementations/stubs required by imported DNS code: `dnlookup`, `rralloc`, `rrfree`, `rrfreelist`, `dnslog`, and allocation helpers.
- Maintains a temporary DN list and frees it when a message walk completes.

Integration:
- Reached from TCP/UDP port 53 demux.
- Includes `../../ndb/dns.h` and copies resource-record helper code from `ndb/dn.c`.

Risks and notes:
- Uses a static `DNSmsg dm`, so decoding state is global and not reentrant.
- `rrfree()` contains `assert(rp->magic = RRmagic)`, assignment rather than comparison, copied from source.
