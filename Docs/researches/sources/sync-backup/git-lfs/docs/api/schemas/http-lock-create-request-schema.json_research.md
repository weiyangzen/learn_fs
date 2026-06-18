<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-request-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-request-schema.json

## Research

This schema documents lock creation requests. The request is an object requiring `path`; it may include `ref` with required `name`. Additional properties are not explicitly disabled at the top level or inside `ref`.

It is a contract artifact for Git LFS locking API documentation and validators. Risks include no path format constraints, optional ref behavior depending on server support, and permissive additional properties that may hide client mistakes. Test signals are schema validation of lock create examples and parity with lock API structs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-request-schema.json -->
