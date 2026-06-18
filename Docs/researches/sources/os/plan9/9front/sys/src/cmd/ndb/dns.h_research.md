# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dns.h

Shared DNS protocol and resolver header for the `ndb` DNS implementation.

Key elements:
- Defines RR type constants, DNS class constants, opcodes, response codes, DNS header flags, EDNS flags, length limits, TTL constants, packet limits, and request timing limits.
- Defines core structures: `Request`, `DN`, `RR`, `SOA`, `Server`, `DNSmsg`, `Area`, and type-specific payload structs for DNSSEC-like and miscellaneous records.
- Defines global configuration `Cfg` for cache, resolver, forwarding, serving, and recursion policy.
- Defines `Stats` counters for query volume, timing buckets, timeouts, cache/negative-answer behavior, and slave high-water mark.
- Declares cross-file functions for cache management, RR allocation/formatting, area management, database lookup, recursive resolution, server response generation, UDP/TCP servers, notify processing, and packet conversion.

Notable behavior:
- `RR` uses unions heavily; fields are interpreted by `type` and `negative`.
- `Request` carries fork/longjmp state and active-mark state for request workers.
- EDNS is modeled as an OPT RR stored separately in `DNSmsg.edns`.
- `Maxactive` is 250, and request processing timeout defaults to 15 seconds.

Risks and quirks:
- Many globals are declared here and defined in different programs, so utility binaries provide stubs or alternate definitions.
- Typo-preserving names like `Runimplimented` are part of the internal API.
