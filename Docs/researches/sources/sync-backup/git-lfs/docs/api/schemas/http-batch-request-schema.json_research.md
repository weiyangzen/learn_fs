<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-request-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-batch-request-schema.json

## Research

This JSON Schema documents the Git LFS HTTPS Batch API request. The top-level object may contain `transfers`, required `operation`, and required `objects`. Each object requires `oid` and nonnegative numeric `size`, may include `authenticated`, and disallows additional properties.

It has no runtime state, but acts as an integration contract for clients, servers, tests, and documentation. Risks are schema/spec drift, loose `operation` string validation, no OID pattern enforcement, and using `number` rather than integer for sizes. Test signals would be schema validation of sample requests and compatibility with actual batch API structs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-request-schema.json -->
