# sources/sync-backup/casync/test/test-caorigin.c

Purpose: tests origin range collection behavior.

Important APIs/types/functions: creates several `CaLocation` objects, pushes them into `CaOrigin`, dumps state, advances bytes, concatenates origins with full and bounded lengths, and validates calls succeed.

Control flow/state: mutable `CaOrigin` holds ordered location spans and byte counts. Operations coalesce/advance/append while preserving location semantics.

Dependencies/integration: covers origin tracking used to map chunks back to source locations.

Risks/test signals: mostly asserts success and dumps diagnostics; it does not compare every intermediate structure against explicit expected values, so semantic coverage is moderate.

Source research group: `subset-b-009122`.
