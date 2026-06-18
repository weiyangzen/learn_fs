<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_metadata_extension_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_metadata_extension_test.rs

Purpose: this E2E regression test validates RustFS’s `GET /{bucket}?versions&metadata=true` extension. It checks that version listing XML includes user metadata, user tags, and internal erasure metadata fields for a versioned object.

Important APIs, types, and functions: `signed_get()` constructs an `http::Request` with `x-amz-content-sha256: UNSIGNED-PAYLOAD`, signs it with `rustfs_signer::sign_v4()`, copies signed headers into `local_http_client().get()`, and returns the raw `reqwest::Response`. The test uses AWS SDK bucket versioning APIs, object metadata/tagging upload, `urlencoding`, `StatusCode`, and raw XML string assertions.

Control flow: the test starts a RustFS server, creates a bucket, enables versioning, uploads one object with user metadata `project=alpha`, `owner=ops` and tags `env=test&project=alpha`, then performs a manually signed GET to `?versions&metadata=true&prefix=<key>`. It asserts HTTP 200 and checks the XML body contains `ListVersionsResult`, a `Version`, `UserMetadata`, stripped metadata keys, escaped `UserTags`, `Internal`, and specific internal `<K>1</K>` and `<M>0</M>` elements.

State and persistence: state includes bucket versioning configuration, one object version, user metadata, tags, and RustFS internal metadata exposed by the extension. The test does not explicitly delete the bucket/object after assertions, relying on temporary environment teardown.

Dependencies and integration points: depends on RustFS S3 versioning, metadata/tag persistence, the custom metadata extension, raw SigV4 signing through `rustfs_signer`, reqwest local HTTP client, and XML response formatting.

Risks: XML validation is string-based and brittle to formatting, ordering, namespaces, or schema changes. It asserts exact internal `K` and `M` values, coupling the test to erasure metadata for the default environment. It does not parse XML or validate multiple versions/delete markers.

Test signals: passing test proves the signed extension endpoint accepts `versions&metadata=true`, returns version-list XML, strips `x-amz-meta-` style user metadata into user-facing XML tags, includes escaped tag data, and exposes expected internal metadata fields.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_metadata_extension_test.rs -->
