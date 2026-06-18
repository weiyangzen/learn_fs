# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.c

## Role

`msgreply.c` converts parsed DNS packets into durable query/reply cache structures, manages reply TTLs and copying, supplies query/reply cache hash callbacks, logs replies, handles EDNS option lists, and dispatches in-place module callbacks.

## Parsing to Durable Reply Data

`parse_create_qinfo()` copies query names out of the packet. `construct_reply_info_base()` allocates a `reply_info` with packed trailing arrays for RRset references and RRset pointers. `reply_info_alloc_rrset_keys()` obtains per-RRset key objects from either a region or special allocator.

`parse_copy_decompress_rrset()` copies a parsed RRset into a `ub_packed_rrset_key`, decompressing owner names and RDATA. `parse_create_rrset()`, `parse_rr_copy()`, and `rdata_copy()` allocate and populate contiguous `packed_rrset_data`, apply TTL caps/floors, handle negative-SOA TTL rules, preserve upstream zero-TTL status, and decompress embedded RDATA names.

`parse_create_msg()` combines query creation, reply allocation, RRset-key allocation, and RR copy/decompression. `reply_info_parse()` is the top-level response parser: it parses the packet, extracts EDNS, creates cacheable data, and returns DNS RCODE-style errors.

## TTL, Cache, and Query Helpers

The file defines global TTL policy defaults such as `MAX_TTL`, `MIN_TTL`, `MAX_NEG_TTL`, `SERVE_EXPIRED_TTL`, and `SERVE_ORIGINAL_TTL`.

`reply_info_set_ttls()` converts relative TTLs to absolute cache times, while `reply_info_absolute_ttls()` forces all reply/RR TTLs to a given absolute value. `reply_info_can_answer_expired()` and `reply_info_could_use_expired()` decide whether expired cache entries can still answer or remain useful.

`query_info_parse()`, `query_info_compare()`, `query_info_hash()`, `query_info_entrysetup()`, `query_info_clear()`, `msgreply_sizefunc()`, `query_entry_delete()`, and `reply_info_delete()` implement query cache key parsing, ordering, hashing, ownership transfer, memory accounting, and cleanup.

`reply_info_copy()` and `repinfo_copy_rrsets()` deep-copy replies and RRsets, including DNSSEC bogus EDE reason strings. `make_new_reply_info()` builds a reduced answer-only reply using shallow-copied RRsets.

## Reply Inspection and Logging

`reply_find_final_cname_target()`, `reply_find_answer_rrset()`, `reply_find_rrset_section_an()`, `reply_find_rrset_section_ns()`, and `reply_find_rrset()` search answer or full reply data, following CNAME chains where appropriate.

`reply_check_cname_chain()` verifies cached CNAME/DNAME chain consistency. `reply_all_rrsets_secure()` checks whether all RRsets have secure validation status. `log_dns_msg()`, `log_reply_info()`, and `log_query_info()` provide wire-format or structured query/reply logging.

## EDNS Options and In-place Callbacks

`edns_opt_list_append()`, `edns_opt_list_append_ede()`, `edns_opt_list_append_keepalive()`, `edns_opt_list_remove()`, copy helpers, comparison helpers, free helpers, and `edns_opt_list_find()` manage region-allocated or malloc-allocated EDNS option lists.

`inplace_cb_reply_call_generic()` and the specific reply/cache/local/servfail wrappers call registered module callbacks after validating callback function pointers through `fptr_ok()`/`fptr_whitelist_*`. Query, EDNS-back-parsed, and query-response callback paths are similarly dispatched.

`local_alias_shallow_copy_qname()` exposes the current single-CNAME local alias assumption by returning the target name from the alias RR’s RDATA.

## Research Notes

This file bridges untrusted packet parsing and long-lived cache storage. Important invariants include decompressed RDATA storage, consistent TTL conversion, ownership transfer of query names into cache entries, RRset trust assignment by section and AA bit, and callback whitelist checks before indirect calls.
