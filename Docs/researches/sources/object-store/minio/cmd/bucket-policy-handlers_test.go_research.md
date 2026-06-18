# Research: sources/object-store/minio/cmd/bucket-policy-handlers_test.go

Purpose: tests bucket creation concurrency and bucket policy HTTP handlers across V4/V2 signed requests, anonymous requests, invalid inputs, and nil object-layer handling.

Important APIs and helpers: helper policy builders create anonymous read/write bucket/object policies. `TestCreateBucket` verifies concurrent `MakeBucket` has exactly one success. `TestPutBucketPolicyHandler`, `TestGetBucketPolicyHandler`, and `TestDeleteBucketPolicyHandler` use request builders, policy templates, `getPutPolicyURL`, `getGetPolicyURL`, `getDeletePolicyURL`, and policy parser equality checks.

Control flow: create-bucket launches 100 goroutines synchronized by a channel and expects one success plus 99 `BucketExists` errors. PUT policy tests valid policy, over-limit content length, zero content length, nil body, empty credentials, malformed JSON, policy resource mismatch, nonexistent/invalid buckets, and empty `Version`. GET tests first install a policy, then fetch valid/nonexistent/invalid buckets and compares parsed policy equality for successful responses. DELETE installs policy, deletes it for valid/nonexistent/invalid buckets, repeats for V2 signing, and checks anonymous/nil object-layer paths.

State and persistence behavior: tests mutate object-layer bucket state and bucket metadata policy state. They verify policy persistence is visible through GET and removable by DELETE. Anonymous tests verify bucket policy changes do not grant access to policy-management APIs.

Dependencies and integration points: integrates object-layer API, HTTP router, signing V2/V4, policy parser, bucket metadata persistence, anonymous access harness, and nil object-layer harness.

Risks: some request bodies are `io.ReadSeeker` instances reused between V4 and V2 requests inside the same test case; depending on request builder behavior, reader position could matter. Exact policy equality is parsed before comparison, reducing JSON ordering brittleness. Tests do not directly inspect metadata updated-at timestamps or replication hooks.

Test signals: strong coverage for policy handler validation and auth behavior. Missing signals include site-replication hook failures, concurrent policy updates, and behavior for chunked/missing content-length transports beyond explicit zero length.
