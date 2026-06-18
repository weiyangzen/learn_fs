# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.h

## Role

`msgreply.h` declares Unbound’s stored DNS query and reply data model plus helper APIs for parsing, copying, TTL handling, lookup, logging, EDNS option lists, and in-place callback dispatch.

## Data Model

`struct query_info` stores the cache-significant question: qname, qname length, qtype, qclass, and optional `local_alias`. The local alias comments document that the current implementation supports a single CNAME-style alias but callers must treat lifetime carefully.

`struct rrset_ref` stores a cached RRset key pointer and its id for lock-ordered validation.

`struct reply_info` stores response flags, authoritative bit, qdcount, reply TTLs, prefetch TTL, serve-expired TTLs, DNSSEC security status, cached EDE bogus reason, section RRset counts, an ordered RRset pointer array, and a trailing `rrset_ref` array used for locking/cache validation.

`struct msgreply_entry` combines a `query_info` cache key with an `lruhash_entry`.

## Public API

The header declares constructors and parsing functions: `construct_reply_info_base()`, `query_info_parse()`, `reply_info_parse()`, `parse_create_msg()`, `parse_reply_in_temp_region()`, `parse_copy_decompress_rrset()`, and `reply_info_alloc_rrset_keys()`.

Cache and lifetime helpers include `reply_info_sortref()`, TTL setters, parse deletion, query comparison/hash/clear, message size accounting, entry setup, reply copying, expired-answer checks, and reduced reply creation.

Search and validation helpers include CNAME target lookup, CNAME-chain checking, all-secure checking, and RRset lookup in answer, authority, or all sections.

Logging helpers expose packet-style and structured query/reply logging. EDNS helpers append, remove, find, copy, compare, and free option lists, including EDE and keepalive convenience functions.

Callback APIs cover reply, cache reply, local reply, SERVFAIL reply, outbound query, EDNS-back-parsed, and query-response callback lists. `local_alias_shallow_copy_qname()` exposes the current alias extraction helper.

## Research Notes

The header’s comments are important for ownership and concurrency: `query_info` names may point into buffers or be allocated; `reply_info` has packed trailing arrays; `rrset_ref` ordering matters for lock acquisition; and local alias data may point to configuration or ephemeral regional memory.
