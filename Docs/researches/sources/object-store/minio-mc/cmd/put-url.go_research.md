# Research: sources/object-store/minio-mc/cmd/put-url.go

## sources/object-store/minio-mc/cmd/put-url.go

Purpose: classifies and prepares source/target `URLs` for `mc put`.

Important APIs and functions: `preparePutURLs` wraps URL preparation in channels; `guessPutURLType` validates supported source/target combinations and selects copy type A or B.

Control flow: `preparePutURLs` calls `guessPutURLType`, maps type A to `prepareCopyURLsTypeA`, type B to `prepareCopyURLsTypeB`, and forwards any errors. `guessPutURLType` supports exactly one source. It stats the source, requires the source client to be filesystem, rejects directories as unsupported type C, requires the target client to be `S3Client`, requires a non-empty bucket, and treats empty or trailing-separator object paths as folder targets.

State and persistence: no direct mutation; emits prepared work that `put-main.go` uploads.

Dependencies and integration: uses alias expansion, `url2Stat`, client constructors, S3 bucket/object parsing, MinIO `ObjectInfo`, and copy URL helpers from the copy subsystem.

Risks and tests: multiple sources are rejected as invalid despite `mainPut` accepting `SOURCE [SOURCE...] TARGET` shape. Error text has a capitalized period style. No direct tests cover put URL classification.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/put-url.go -->
