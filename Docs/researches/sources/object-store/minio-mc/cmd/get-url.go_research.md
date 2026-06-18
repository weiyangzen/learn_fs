# sources/object-store/minio-mc/cmd/get-url.go

Purpose: Prepares URL pairs for `mc get`.

Important APIs/types/functions: `prepareGetURLs` and `guessGetURLType`.

Control flow: `guessGetURLType` requires exactly one source, verifies the source client is `S3Client`, requires bucket and object path, creates source content from object info and optional version ID, verifies the target is an `fsClient`, then classifies target as file-to-file or file-to-directory. `prepareGetURLs` delegates to copy type A/B preparation.

State and persistence: Stateless preparation; no actual download here.

Dependencies/integration: Reuses copy URL structs and helpers, `newClient`, `S3Client`, `fsClient`, and minio object info.

Risks: Error strings are plain `fmt.Errorf` wrapped by probe in some cases. It constructs source content without an initial stat/read, so missing remote objects surface later.

Test signals: No direct tests.
