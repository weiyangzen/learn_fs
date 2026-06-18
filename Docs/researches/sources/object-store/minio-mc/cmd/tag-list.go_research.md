<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-list.go -->
# sources/object-store/minio-mc/cmd/tag-list.go

Purpose: implements `mc tag list`, listing bucket/object tags for a target, optional versions, rewind time, and recursive object traversal.

Important APIs/types/functions: `tagListFlags`, `tagListCmd`, `tagListMessage`, `parseTagListSyntax`, `showTags`, `showTagsSingle`, and `mainListTag`.

Control flow: syntax validation requires one target, rejects simultaneous `--version-id` and `--rewind`, parses rewind, and infers current UTC time when `--versions` is set without rewind. For a single non-recursive object/bucket, it calls `GetTags` directly. Recursive/versioned mode lists objects with `ListOptions`, skips delete markers, stops at the target when not recursive, and invokes `showTagsSingle` per content item.

State and persistence: read-only against S3/MinIO tag state.

Dependencies and integration points: depends on generic `Client` tag APIs, alias expansion/client creation, list traversal, `parseRewindFlag`, `minio.ToErrorResponse` for `NoSuchTagSet`, and colorized/JSON output.

Risks and test signals: recursive/versioned traversal can produce many per-object client creations. Tests should cover empty tag sets, version-id vs rewind validation, delete-marker skipping, recursive boundaries, sorted text output, and JSON schema.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-list.go -->
