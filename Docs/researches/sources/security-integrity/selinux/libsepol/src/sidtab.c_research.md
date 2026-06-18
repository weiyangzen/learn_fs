# sources/security-integrity/selinux/libsepol/src/sidtab.c

## Purpose
`sidtab.c` implements the SID-to-context table used by libsepol services to resolve, intern, enumerate, convert, and destroy security IDs.

## Important APIs and Control Flow
The table is a fixed-size hash array indexed by `sid & SIDTAB_HASH_MASK`, with each bucket sorted by SID. Insert rejects duplicate SIDs and deep-copies contexts. Search returns a matching context or remaps unknown SIDs to `SECINITSID_UNLABELED` when available. `sepol_sidtab_context_to_sid()` scans for an existing context, then allocates `next_sid` unless shutdown or exhausted. Map-remove deletes nodes whose callback returns nonzero.

## State and Integration
State includes `htable`, `nel`, `next_sid`, and `shutdown`. `services.c` uses the table for all SID lookup, object-context SID caching, and policy reload conversion.

## Risks and Test Signals
Lock macros are empty in this implementation, so double-check locking is not real synchronization. Context lookup is O(number of SIDs). `sepol_sidtab_set()` transfers pointers without deep copy. Tests should cover duplicate insert, unlabeled remap, allocation after explicit insert, shutdown, map-remove, and policy reload ownership transfer.
