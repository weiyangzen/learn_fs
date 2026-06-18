# sources/security-integrity/selinux/libsepol/src/nodes.c

## Purpose
Implements policydb operations for node contexts: count, exists, query, modify/add, and iterate. It bridges high-level `sepol_node_t` records to low-level `ocontext_t` entries in `policydb->ocontexts[OCON_NODE]` and `policydb->ocontexts[OCON_NODE6]`.

## Important APIs, Types, and Functions
Internal converters are `node_from_record()` and `node_to_record()`, using context conversion helpers. Public operations are `sepol_node_count`, `sepol_node_exists`, `sepol_node_query`, `sepol_node_modify`, and `sepol_node_iterate`.

## Control Flow
`node_from_record()` allocates an `ocontext_t`, clones binary address/mask from the record, stores them in IPv4 or IPv6 union fields based on protocol, converts the high-level context to a policydb `context_struct_t`, and returns ownership to the caller. `node_to_record()` does the reverse. Exists/query unpack the key and scan the matching IPv4 or IPv6 list with `memcmp`. Modify converts the record and prepends it to the matching list. Iterate walks IPv4 first, then IPv6, converts each low-level node to a record, calls the callback, and stops early on positive callback status.

## State and Persistence Behavior
The persistent policy state is the linked list inside `policydb_t`. `sepol_node_modify()` only prepends; it does not replace or remove an existing matching node even though it accepts a key. Query/exists see the first matching entry by list order. Contexts are copied into low-level policydb storage and freed through policydb destruction.

## Dependencies and Integration Points
Depends on `sepol/policydb/policydb.h` ocontext layout, record APIs from `node_internal.h`, and context conversion helpers from `context.h`. It integrates with binary policy read/write through the shared `ocontexts` arrays and with CIL conversion through nodecon emitters in `module_to_cil.c`.

## Risks and Edge Cases
`sepol_node_modify()` ignores key address/mask when building the stored node and only uses key protocol to choose the list, so callers can provide a key and data that disagree. Duplicate entries are possible because modify does not check existing entries. Byte lengths are assumed to be valid for protocol; malformed records can cause partial or overbroad `memcpy` into low-level fields. Callback errors during iteration abort after freeing the current record.

## Test Signals
Tests should cover IPv4/IPv6 count/query/exists, modify plus query round trip, duplicate modify behavior, key/data mismatch, callback early exit, callback error cleanup, and conversion of invalid protocol or malformed byte-size records.
