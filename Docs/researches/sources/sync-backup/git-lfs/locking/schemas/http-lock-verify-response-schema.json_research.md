# sources/sync-backup/git-lfs/locking/schemas/http-lock-verify-response-schema.json

Purpose: JSON Schema draft-04 contract for HTTPS lock verification responses.

Important API fields: required `ours` and `theirs` arrays of lock objects. Defined locks require `id` and `path`; `locked_at` and `owner.name` are optional. `next_cursor` supports pagination.

Control flow: not executable; validates responses used by `SearchLocksVerifiable`.

State/persistence behavior: unlimited verify results can be encoded into the `verifiable` JSON cache and also repopulate the in-memory lock cache.

Dependencies/integration: maps to `lockVerifiableList`, `Lock`, and pre-push/verify workflows that distinguish current-user locks from conflicting locks.

Risks: `owner` and `locked_at` are optional for compatibility, so callers must not assume complete metadata. Pagination correctness depends on server-provided `next_cursor`.

Test signals: schema tests catch missing `ours`/`theirs` arrays and incompatible lock field types.
