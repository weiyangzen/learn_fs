# sources/object-store/minio/cmd/erasure-object-conditional_test.go

Purpose: regression tests for conditional single PUT behavior when existing-object metadata cannot be read with quorum. The intended invariant is that `PutObject` with conditional headers must fail with a read quorum error instead of overwriting or misclassifying the object state.

Important APIs and functions under test: `PutObject`, `GetObjectInfo`, `prepareErasure16`, `isErrReadQuorum`, `ObjectOptions.CheckPrecondFn`, and HTTP metadata keys `xhttp.IfNoneMatch`/`xhttp.IfMatch`.

Control flow: the test creates a 16-disk erasure setup, uploads an initial object, reads its ETag, then overrides the first eight disks to `nil` while holding the erasure disk mutex. Three subtests try `If-None-Match: *`, correct `If-Match`, and wrong `If-Match`, each using a `CheckPrecondFn` that would normally evaluate object info.

State and persistence behavior: uses real temporary erasure roots and a real object, then simulates disk outage through the set disk function. No final cleanup beyond standard shutdown/root removal is needed.

Dependencies and integration points: directly exercises the precondition branch at the start of `erasureObjects.putObject`, which calls `getObjectInfo` under the object namespace lock. It depends on read quorum calculations from `erasure-metadata.go` and disk availability behavior in the erasure set.

Risks: disk-slice mutation is intentionally invasive and should remain isolated. The second subtest does not set `HasIfMatch`, while the multipart variant does for some cases; this still covers read-quorum propagation through `CheckPrecondFn`, but `HasIfMatch`-specific logic is less directly tested here.

Test signals: protects issue 21603 for single-object PUT. The key signal is that all conditional writes return read quorum errors when the existing object cannot be verified.
