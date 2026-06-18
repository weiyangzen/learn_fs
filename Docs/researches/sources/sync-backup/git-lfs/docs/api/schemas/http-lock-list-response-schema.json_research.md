<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-list-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-list-response-schema.json

## Research

This schema defines lock list responses. The response requires `locks`, an array of lock objects with optional `id`, `path`, `locked_at`, and `owner.name`, and may include `next_cursor` for pagination.

It is a non-executable API contract artifact. Risks include weak lock item requirements compared with create/verify schemas, no date format, no pagination type beyond string, and permissive additional properties. Test signals are validation of list responses with and without pagination and parity with API documentation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-list-response-schema.json -->
