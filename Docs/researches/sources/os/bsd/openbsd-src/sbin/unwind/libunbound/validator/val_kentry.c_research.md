# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.c

## Purpose
Implements validator key-entry storage, copying, comparison, construction, and conversion routines used by the key cache and validation pipeline.

## Main Responsibilities
- Provides slabhash/lruhash callbacks for size, compare, delete-key, and delete-data.
- Hashes key entries by class and domain name.
- Deep-copies key entries either to malloc storage or to a regional allocator.
- Represents three key-entry states: good key rrset, bad key with reason/EDE, and null/insecure entry.
- Creates key entries from null, bad, and rrset inputs.
- Converts a stored key entry back into a region-allocated packed rrset.
- Computes the smallest ZSK key size in a good DNSKEY rrset.

## Key Functions
- `key_entry_sizefunc`: estimates memory use including name, data, lock, rrset data, reason, and algorithm list.
- `key_entry_compfunc`: orders entries by class and query dname.
- `key_entry_hash`: class plus dname lookup3 hash.
- `key_entry_copy_toregion`: region deep-copy for query processing.
- `key_entry_copy`: malloc deep-copy for cache insertion.
- `key_entry_isnull`, `key_entry_isgood`, `key_entry_isbad`: state predicates.
- `key_entry_create_null`, `key_entry_create_rrset`, `key_entry_create_bad`: constructors.
- `key_entry_get_rrset`: reconstructs a `ub_packed_rrset_key` from stored data.
- `key_entry_keysize`: scans DNSKEY records for ZSK flags and returns smallest supported key size calculation.

## Dependencies and Integration
Uses packed rrset utilities, dname comparison/hash helpers, regional allocation, network byte-order helpers, and sldns raw DNSKEY key-size routines. The resulting objects are consumed by `val_kcache` and DNSSEC validation code.

## Notable Constraints and Risks
- Region constructors intentionally tolerate failure to store optional reason strings.
- `key_entry_copy` conditionally copies the reason string based on `copy_reason`; callers decide whether cached entries own that diagnostic text.
- Algorithm list memory is treated as NUL-terminated string data for size/copy purposes.
