# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dn.c

Core DNS cache, domain-name table, RR allocation/copy/free, activity accounting, formatting, and aging logic. It owns the global `DN *ht[HTLEN]` hash table, `dnlock`, RR type/response/opcode name tables, stats dumping, and most shared memory lifecycle rules.

`dnlookup()` interns domain names by case-insensitive hash. `rrattach()` and `rrattach1()` insert RRs into a domain’s list while preserving type grouping, authority priority, duplicate suppression, negative/positive replacement, PTR ordering, and anti-spoof rules for local cached-db zones. `rrlookup()` returns copied records in priority order: authoritative DB, live authoritative network, live unauthoritative network, unauthoritative DB, then fallback positives.

Aging and cleanup are present but effectively disabled by huge defaults because comments say prior aging corrupted the cache. Functions still exist for explicit aging, DB-record expiration, mark/sweep of unreferenced names, and “never age” marking for DB-derived roots.

Activity control (`getactivity()`/`putactivity()`) gates concurrent resolver work and runs refresh/aging only when alone. `slave()` forks shared-memory workers for blocking work, with explicit comments about avoiding deadlock and stack-copy assumptions.

Formatting functions `%R` and `%Q` print human-readable and attribute-value forms of RRs. Allocation helpers handle deep copies and freeing for SOA/SRV/KEY/SIG/CERT/NULL/TXT payloads, with magic fields and memory poisoning for bug detection.

Risks are high because many modules depend on `dnlock` discipline and shared `RR` ownership semantics. Several helpers abort if called without expected locks. Forking with shared memory, `setjmp`, cached pointers, and disabled aging all make this a fragile but central subsystem.
