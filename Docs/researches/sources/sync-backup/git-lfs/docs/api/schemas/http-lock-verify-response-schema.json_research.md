<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-verify-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-verify-response-schema.json

## Research

This schema defines lock verification responses. It requires `ours` and `theirs` arrays, each containing lock objects from a shared definition. A lock requires `id` and `path`, and may include `locked_at` and `owner.name`. `next_cursor` supports pagination.

The schema has no runtime state but is central to push lock verification semantics because `theirs` drives upload rejection/warnings and `ours` can prompt unlock hints. Risks include `locked_at` optionality, no owner requirement, no date format, and permissive additional properties. Test signals should cover empty arrays, paginated responses, and responses containing unowned locks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-verify-response-schema.json -->
