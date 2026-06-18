# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.h

## Role

`packed_rrset.h` defines Unbound’s cacheable RRset key/data structures, RRset flags, trust/security enums, and utility APIs for packed RRset lifecycle and inspection.

## Structures and Flags

`rrset_id_type` is a 64-bit unique RRset id. Flags distinguish NSEC-at-apex, parent-side glue, negative-SOA copies, fixed TTL data, RPZ synthetic data, unverified glue, and upstream zero-TTL RRsets. `RR_COUNT_MAX` bounds RR/RRset counts for overflow protection.

`struct packed_rrset_key` contains owner dname, dname length, flags, network-order type, and network-order class. `struct ub_packed_rrset_key` wraps that key with an `lruhash_entry` and id for cache use.

`enum rrset_trust` ranks data trust from none through additional/authority/answer variants, glue, primary/zone-transfer data, DNSSEC validated data, and ultimate trust. `enum sec_status` records validation state from unchecked through bogus, indeterminate, insecure, sentinel fail, and secure.

`struct packed_rrset_data` stores TTL metadata, RR/RRSIG counts, trust/security state, and arrays for RDATA length, per-RR TTL, and RDATA pointers. Its memory layout is designed for one contiguous cache allocation: base struct, arrays, then uncompressed wire-format RDATA blobs.

## API Surface

The header declares parse cleanup, memory sizing, TTL access, cache compare/delete callbacks, data equality, hash calculation, pointer fixup, TTL add, CNAME/DNAME target extraction, enum stringification, logging, RR-to-string conversion, regional and allocator copies, and raw RDATA lookup.

## Research Notes

The key/data split supports cache replacement and locking. Callers must know that RDATA begins with a network-order rdlength field, RRSIGs are stored after ordinary RRs, and copied contiguous blobs require `packed_rrset_ptr_fixup()` before use.
