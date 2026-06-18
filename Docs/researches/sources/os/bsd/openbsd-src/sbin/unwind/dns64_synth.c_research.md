# File Research: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.c

OpenBSD `unwind` DNS64 synthesis helper adapted from Unbound’s DNS64 module. It exports `dns64_synth_aaaa_data()` for frontend-side DNS64 response rewriting.

Key behavior:
- Uses global `dns64_prefixes` and `dns64_prefix_count` from `frontend.c`.
- Synthesizes one AAAA record per configured DNS64 prefix for each source A record.
- Preserves TTL, trust, and security metadata from the source A rrset.
- Constructs a replacement `ub_packed_rrset_key` with type `AAAA` and recomputed hash.
- Validates source A rdata shape as 2-byte rdatalen plus 4-byte IPv4 address.
- Uses Unbound regional allocation, so synthesized data lifetime is tied to the query region.

Important implementation detail:
- `synthesize_aaaa()` copies the IPv6 prefix, inserts the IPv4 address at `prefixlen / 8`, and skips byte position 8 per DNS64 address format handling.

Role in group:
- This is the OpenBSD-specific multi-prefix variant used by `frontend.c` when `unwind` receives an empty AAAA result and retries the same name as A.
