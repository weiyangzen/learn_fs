# Research: sources/object-store/minio-mc/cmd/mirror-url.go

## sources/object-store/minio-mc/cmd/mirror-url.go

Purpose: prepares mirror copy/remove work by validating source/target syntax, applying exclude rules, comparing source and target listings, and emitting `URLs` tasks.

Important APIs and types: `checkMirrorSyntax`, `matchExcludeOptions`, `matchExcludeBucketOptions`, `deltaSourceTarget`, `mirrorOptions`, and `prepareMirrorURLs` are the core functions. `mirrorOptions` is the shared option bag consumed by listing, filtering, copying, and watch logic.

Control flow: syntax validation enforces exactly two arguments, warns on deprecated `--force`, checks preserve limitations on Windows, stats non-watch sources, ensures non-watch sources are directories, and absolutizes local source paths. `deltaSourceTarget` normalizes trailing separators, expands aliases, creates clients, compares objects with `objectDifference`, filters source and target suffixes by object, bucket, and storage-class options, then emits copy, overwrite-denied, remove, or error `URLs`.

State and persistence: this file does not mutate storage directly. It creates channels and client/listing state only; the generated work drives mutations in `mirror-main.go`.

Dependencies and integration: depends on alias expansion, URL typing, `url2Stat`, `objectDifference`, wildcard matching, MinIO checksum type, and shared error constructors.

Risks and tests: path prefix trimming is sensitive to slash normalization and Windows separators. Exclude matching is wildcard-based and operates on suffixes/bucket names. No direct tests cover mirror URL generation in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mirror-url.go -->
