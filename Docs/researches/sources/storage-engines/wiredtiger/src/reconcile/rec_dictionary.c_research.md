<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_dictionary.c -->
# sources/storage-engines/wiredtiger/src/reconcile/rec_dictionary.c

## Purpose
Maintains the per-page reconciliation dictionary used to replace repeated values with copy cells.

## Important APIs, Types, and Functions
`__wti_rec_dictionary_init`, `__wti_rec_dictionary_free`, `__wti_rec_dictionary_reset`, and `__wti_rec_dictionary_lookup`. Internal skiplist helpers search, build insert stacks, and insert by hash.

## Control Flow
Initialization frees any prior dictionary, allocates a fixed slot array, and gives each slot a random skiplist depth. Reset clears the skiplist heads and next-slot counter at restart/page boundary. Lookup hashes the candidate value, scans matching hashes, uses `__wt_cell_pack_value_match` to confirm exact packed-cell equality, returns a match if found, or inserts a new dictionary entry if slots remain.

## State and Persistence Behavior
Dictionary state is in-memory and scoped to the current reconciliation page. Matching entries cause output cells to reference earlier values in the same disk image; no standalone persistent dictionary exists.

## Dependencies and Integration Points
Used by reconciliation value-cell builders for row/column pages when dictionary compression is enabled. Depends on CityHash, skiplist depth selection, and current reconciliation image offsets.

## Risks and Edge Cases
Hash collisions require exact cell comparison. Once slots are exhausted, new values are not added but existing entries remain usable. Reset must happen at page boundaries to avoid cross-page references.

## Test Signals
Dictionary compression tests should include repeated values, hash collision simulation, slot exhaustion, restart/reset behavior, and validation that copy offsets refer to same-page cells.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_dictionary.c -->
