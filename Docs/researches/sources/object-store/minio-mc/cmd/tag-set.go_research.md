<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-set.go -->
# sources/object-store/minio-mc/cmd/tag-set.go

Purpose: implements `mc tag set`, assigning tags to a bucket/object or to multiple object versions recursively.

Important APIs/types/functions: `tagSetFlags`, `tagSetCmd`, `tagSetMessage`, `parseSetTagSyntax`, `setTags`, `setTagsSingle`, and `mainSetTag`.

Control flow: validation requires `TARGET TAGS`, rejects `--version-id` with rewind/versions, and requires `--exclude-folders` to be paired with `--recursive`. Single mode calls `SetTags` on one client. Recursive/versioned mode lists matching objects, skips delete markers, optionally skips folder-like objects when `excludeFolders` is set, respects non-recursive target boundary, and applies tags per content item/version.

State and persistence: mutates remote tag state through `Client.SetTags`; tags string format is passed through to client implementation.

Dependencies and integration points: uses list traversal, alias/client helpers, URL bucket/object parsing, rewind parsing, global context, and JSON/text output.

Risks and test signals: recursive tagging can affect many objects and the folder exclusion check is path-separator based. Tests should cover invalid flag combinations, tag string validation via client errors, version handling, delete-marker skipping, folder exclusion, and JSON schema.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-set.go -->
