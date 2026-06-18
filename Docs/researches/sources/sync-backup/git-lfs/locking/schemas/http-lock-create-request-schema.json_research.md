# sources/sync-backup/git-lfs/locking/schemas/http-lock-create-request-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS lock creation requests.

Important API fields: top-level object with required `path` string and optional `ref` object. `ref`, when present, contains required `name` string.

Control flow: not executable; consumed by API tests to validate serialized lock creation payloads.

State/persistence behavior: no local state. It defines the client-to-server wire shape used before a lock exists on the server.

Dependencies/integration: aligns with `lockRequest` and `lockRef` in the locking API implementation.

Risks: the schema does not constrain path format, ref namespace, or additional properties. Servers must enforce semantic validation separately.

Test signals: schema validation should fail if `path` is absent or a provided `ref` lacks `name`.
