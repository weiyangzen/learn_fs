<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-delete-request-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-delete-request-schema.json

## Research

This schema documents lock deletion request bodies. It allows optional `force` boolean and optional `ref` object with required `name` if present. No top-level fields are required.

The schema is used as API documentation/validation and has no executable state. Risks include permissive additional properties, no explicit lock ID because the ID is typically in the URL path, and no constraints on ref naming. Test signals should validate force and non-force examples against client/server request structs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-delete-request-schema.json -->
