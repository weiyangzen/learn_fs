# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.c

## Role

`packed_rrset.c` implements memory management, hashing, comparison, copying, TTL adjustment, target extraction, logging, and lookup helpers for Unbound’s packed RRset representation.

## Key Behavior

`ub_packed_rrset_parsedelete()`, `ub_rrset_key_delete()`, and `rrset_data_delete()` clean up RRset key/data objects and return special keys to the allocator. `ub_rrset_sizefunc()` and `packed_rrset_sizeof()` report memory usage for cache accounting.

`ub_rrset_compare()` orders RRset keys by type, owner-name length/name, class, and flags. `rrset_key_hash()` hashes owner name, host-order type, network-order class, and flags; comments require it to match parser hashing in `msgparse.c`. `rrsetdata_equal()` compares raw RDATA/RRSIG contents while ignoring trust and TTL metadata.

`packed_rrset_ptr_fixup()` repairs internal array pointers after copying a contiguous `packed_rrset_data` blob. `packed_rrset_ttl_add()` adds an absolute-time offset to RRset and per-RR TTLs.

`get_cname_target()` extracts a CNAME or DNAME target from the first RR’s RDATA after validating rdlength and dname format. `ub_packed_rrset_ttl()` returns the RRset TTL.

## Copying and Diagnostics

`packed_rrset_copy_region()` copies an RRset into a regional allocator and optionally converts absolute TTLs back to relative TTLs, including serve-expired calculations and the NS special case for ghost-attack mitigation. `packed_rrset_copy_alloc()` malloc/special-allocates a copy and converts relative TTLs to absolute by adding `now`.

`rrset_trust_to_string()` and `sec_status_to_string()` stringify trust/security enums. `packed_rr_to_string()` reconstructs a single RR wire image and formats it with `sldns_wire2str_rr_buf()`. `log_rrset_key()` and `log_packed_rrset()` log keys and all RR/RRSIG data.

`packed_rrset_find_rr()` searches ordinary data RRs by raw RDATA bytes and length.

## Research Notes

The packed data layout relies on contiguous allocation followed by pointer fixup after `memdup` or regional copy. Hash compatibility with `msgparse.c` is a cross-file invariant, and TTL conversion differs depending on whether the copy is for cache storage or response assembly.
