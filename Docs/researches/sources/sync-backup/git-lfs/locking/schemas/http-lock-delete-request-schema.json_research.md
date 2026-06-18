# sources/sync-backup/git-lfs/locking/schemas/http-lock-delete-request-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS unlock/delete requests.

Important API fields: optional `force` boolean and optional `ref` object with required `name` when `ref` is present. There are no top-level required properties.

Control flow: not executable; validates the body sent by `Unlock`.

State/persistence behavior: no direct persistence. Server response determines whether local lock cache is updated and file permissions are changed.

Dependencies/integration: aligns with `unlockRequest` and ref-aware unlock behavior.

Risks: the schema permits an empty object, so callers can omit both force and ref. Semantic authorization and branch/ref enforcement are server responsibilities.

Test signals: schema validation catches wrong `force` type or malformed `ref`, but not missing lock id because the id is encoded in the URL path, not this body.
