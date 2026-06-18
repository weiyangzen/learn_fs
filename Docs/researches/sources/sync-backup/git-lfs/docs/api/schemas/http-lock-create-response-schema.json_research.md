<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-response-schema.json

## Research

This schema defines lock creation responses. The top-level object requires `lock`; `lock` requires `id`, `path`, and `locked_at`, and may include an `owner` object with `name`. Error-style metadata fields `message`, `request_id`, and `documentation_url` are also allowed.

There is no runtime state. Integration is API documentation and compatibility validation for lock clients/servers. Risks are no date-time format validation for `locked_at`, owner not required, no `additionalProperties: false`, and overlap between success and error metadata in the same schema.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-response-schema.json -->
