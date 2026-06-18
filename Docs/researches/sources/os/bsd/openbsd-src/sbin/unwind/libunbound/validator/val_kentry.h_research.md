# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_kentry.h

## Purpose
Defines validator key-entry structures and declares helper functions for key cache storage and DNSSEC validation.

## Main Types
- `struct key_entry_key`: lruhash key containing hash entry, key name, name length, and DNS class.
- `struct key_entry_data`: cached key state containing absolute TTL, optional rrset data, reason string, EDE code, algorithm list, rrset type, and bad-key flag.

## Represented States
- Good key: `isbad == 0` and `rrset_data != NULL`.
- Bad key: `isbad == 1`.
- Null/insecure entry: `isbad == 0` and `rrset_data == NULL`.

## Public API
Includes lruhash callbacks, hashing, malloc/region copy helpers, state predicates, reason/EDE accessors, constructors for null/good/bad entries, rrset reconstruction, and key-size calculation.

## Integration
This header is the contract between the validator cache (`val_kcache`), packed rrset storage, and validator chain logic.

## Notable Constraints
Function comments specify whether returned objects are malloc-owned, region-owned, or references to entry-owned data. Correct allocator ownership matters for avoiding leaks or invalid frees.
