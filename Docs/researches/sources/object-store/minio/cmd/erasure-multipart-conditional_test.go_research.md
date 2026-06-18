# sources/object-store/minio/cmd/erasure-multipart-conditional_test.go

Purpose: regression tests for conditional multipart APIs when the existing object cannot be read with quorum. It specifically verifies that conditional requests do not proceed or degrade into object-not-found decisions when MinIO cannot reliably evaluate `If-Match` or `If-None-Match`.

Important APIs and functions under test: `NewMultipartUpload`, `CompleteMultipartUpload`, `PutObject`, `PutObjectPart`, `GetObjectInfo`, `prepareErasure16`, `isErrReadQuorum`, and `ObjectOptions.CheckPrecondFn`/`HasIfMatch`. It also uses `xhttp.IfNoneMatch`, `xhttp.IfMatch`, multipart `CompletePart`, and `humanize.MiByte`.

Control flow: each test creates a 16-disk erasure layer, uploads an initial object, captures its ETag, then overrides the set's disk getter to nil out the first eight disks. With EC 8+8, this leaves only eight disks where read quorum is nine. Subtests run conditional initiate and complete paths with `if-none-match`, correct `if-match`, and wrong `if-match` cases.

State and persistence behavior: the tests create real bucket/object/multipart state in temporary erasure roots. They mutate the in-memory disk view through `erasureDisksMu` to simulate a read quorum failure without physically deleting data.

Dependencies and integration points: directly exercises conditional branches in `erasure-multipart.go`, which call `getObjectInfo` before initiating or completing multipart operations. It depends on object-layer locking and read quorum semantics from `erasure-object.go` and `erasure-metadata.go`.

Risks: the test manipulates shared disk slice contents in place; this is acceptable for isolated tests but requires care if helpers begin sharing disk slices across subtests. The second `NewMultipartUpload` wrong-ETag subtest logs instead of failing when a non-read-quorum error appears, so that scenario is a weaker guard than the surrounding cases.

Test signals: protects issue 21603 behavior: conditional multipart operations must return read quorum errors when preconditions cannot be evaluated. It covers both initiate and complete operations.
