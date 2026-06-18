# Research: sources/object-store/minio-mc/cmd/put-main.go

## sources/object-store/minio-mc/cmd/put-main.go

Purpose: implements `mc put`, uploading one or more local files to an S3 object target with multipart, checksum, storage class, encryption, and progress support.

Important APIs and functions: `putFlags`, `putCmd`, `mainPut`, `printPutURLsError`, and `showLastProgressBar`.

Control flow: `mainPut` validates argument count, parses part size and thread count, encryption keys, checksum, storage class, and source/target arguments. A goroutine prepares `URLs` via `preparePutURLs`, updates total byte/object counts and progress total, and sends work to `putURLsCh`. The main loop handles context cancellation, preparation errors, and calls `doCopy` for each upload with multipart size/thread settings and optional `if-not-exists`.

State and persistence: writes objects to the target. Progress totals are mutable local state. No local config mutation.

Dependencies and integration: depends on `preparePutURLs`, `doCopy`, transfer progress readers, humanize parsing, checksum parsing, SSE validation, and shared copy URL structs.

Risks and tests: the preparer goroutine updates `totalBytes` and `pg` while the main goroutine may read/finish progress. Only local file sources and S3 targets are accepted by `put-url.go`. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/put-main.go -->
