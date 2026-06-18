# sources/sync-backup/git-lfs/locking/schemas/http-lock-create-response-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS lock creation responses.

Important API fields: required top-level `lock` object. A lock requires `id`, `path`, and `locked_at`; optional `owner.name` can identify the creator. Optional top-level error/context fields are `message`, `request_id`, and `documentation_url`.

Control flow: not executable; validates the response shape that `LockFile` decodes into `lockResponse` and then caches.

State/persistence behavior: successful responses become local `Lock` records in cache and may influence file writability.

Dependencies/integration: mirrors `Lock`, `User`, and response message handling in the locking client.

Risks: `locked_at` is only typed as string, not format-checked as RFC3339. Owner is not required, while SSH parsing requires owner fields, so transport contracts are not identical.

Test signals: schema tests should catch missing `lock`, missing core lock fields, or type drift.
