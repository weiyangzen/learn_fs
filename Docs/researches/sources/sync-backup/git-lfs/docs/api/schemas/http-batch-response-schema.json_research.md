<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-batch-response-schema.json

## Research

This schema defines the Git LFS HTTPS Batch API response. It requires `objects`; each object requires `oid` and nonnegative `size`, can carry `authenticated`, `actions`, or `error`. An `action` requires `href` and may include headers, `expires_in`, and `expires_at`. Top-level response metadata includes `transfer`, `message`, `request_id`, and `documentation_url`.

The schema is documentation/validation state only. Integration points are batch transfer clients/servers and API docs. Risks include permissive string fields, `expires_at` not date-formatted, `expires_in` allowing negative values, numeric sizes/codes rather than integers, no OID pattern, and `additionalProperties: false` potentially rejecting future protocol extensions unless versioned.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-response-schema.json -->
