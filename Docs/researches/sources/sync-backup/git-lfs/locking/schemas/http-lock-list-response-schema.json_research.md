# sources/sync-backup/git-lfs/locking/schemas/http-lock-list-response-schema.json

Purpose: JSON Schema draft-04 contract for HTTPS lock list responses.

Important API fields: required `locks` array, with each item carrying optional `id`, `path`, `locked_at`, and `owner.name`. `next_cursor` supports pagination.

Control flow: not executable; validates list responses consumed by `SearchLocks` and remote pagination.

State/persistence behavior: unlimited unfiltered list responses can be persisted into the `remote` JSON cache file.

Dependencies/integration: maps to `lockList` and `Lock` structures used by the HTTP lock client.

Risks: item fields are not required in this schema, so structurally valid but semantically incomplete locks may pass validation and then cause downstream ambiguity. `locked_at` format is not constrained.

Test signals: schema validation catches missing `locks` or non-array response shapes.
