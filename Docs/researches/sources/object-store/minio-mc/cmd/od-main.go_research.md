# Research: sources/object-store/minio-mc/cmd/od-main.go

## sources/object-store/minio-mc/cmd/od-main.go

Purpose: implements the hidden or specialized `mc od` command for measuring single-stream upload/download/copy throughput with explicit part sizing and skip controls.

Important APIs and types: `odCmd` defines operands `if=`, `of=`, `size=`, `parts=`, and `skip=`; `odMessage` implements CLI/JSON output; `getOdUrls`, `odCheckType`, and `mainOD` route to transfer implementations.

Control flow: `mainOD` validates that operands exist, parses each argument as a `key=value` pair into `argKVS`, resolves source and target with `getOdUrls`, then calls `odCheckType`. Direction is inferred from aliases: S3-to-filesystem uses `odDownload`; filesystem-to-S3, S3-to-S3, and filesystem-to-filesystem use `odCopy` with an `odType` string.

State and persistence: copies or downloads data to the requested target. It does not persist local CLI config beyond normal startup behavior.

Dependencies and integration: reuses copy URL classification (`guessCopyURLType`, `makeCopyContentTypeA`), transfer helpers in `od-stream.go`, `printMsg`, and JSON formatting.

Risks and tests: operand parsing assumes every argument contains `=` and indexes `kv[1]`, so malformed operands can panic. There are no direct tests for `od` in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/od-main.go -->
