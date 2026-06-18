<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-remove.go -->
# sources/object-store/minio-mc/cmd/tag-remove.go

Purpose: implements `mc tag remove`, deleting bucket/object tags, optionally across versions and recursively.

Important APIs/types/functions: `tagRemoveFlags`, `tagRemoveCmd`, `tagRemoveMessage`, `parseRemoveTagSyntax`, `deleteTags`, `deleteTagsSingle`, and `mainRemoveTag`.

Control flow: syntax validation requires one target and rejects `--version-id` combined with `--rewind` or `--versions`. Single non-recursive mode creates one client and calls `DeleteTags`. Recursive/versioned mode lists objects with time/version options, skips delete markers, respects non-recursive target boundary, and deletes tags for each listed object version.

State and persistence: mutates remote bucket/object tag state by calling `Client.DeleteTags`.

Dependencies and integration points: uses alias expansion, `newClient`/`newClientFromAlias`, list traversal, `parseRewindFlag`, global context, colorized/JSON output, and probe errors.

Risks and test signals: broad recursive deletes are destructive. Tests should cover argument validation, version delete targeting, recursive traversal boundaries, delete-marker skipping, client creation errors, and JSON/text output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-remove.go -->
