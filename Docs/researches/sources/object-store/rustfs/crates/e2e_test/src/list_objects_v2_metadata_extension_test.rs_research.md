# sources/object-store/rustfs/crates/e2e_test/src/list_objects_v2_metadata_extension_test.rs

Purpose: End-to-end regression coverage for RustFS's nonstandard ListObjectsV2 metadata extension exposed by `GET /{bucket}?list-type=2&metadata=true`. It verifies that object user metadata, object tags, and internal placement fields are serialized in the listing XML response.

Important APIs/types/functions: The file uses `RustFSTestEnvironment`, `init_logging`, `local_http_client`, `reqwest::StatusCode`, `http::header::HOST`, `rustfs_signer::sign_v4`, `rustfs_signer::constants::UNSIGNED_PAYLOAD`, `s3s::Body`, and `urlencoding::encode`. The helper `signed_get` builds a raw HTTP GET request, signs it with AWS Signature V4, copies signed headers into a reqwest request, and sends it through the local HTTP client.

Control flow: The test starts RustFS, creates a bucket, uploads `objects/metadata-object.txt` with user metadata `project=alpha` and `owner=ops`, sets tags `env=test&project=alpha`, then manually requests the list-type=2 endpoint with `metadata=true` and a URL-encoded prefix matching the object key. It asserts HTTP 200, reads the XML text body, logs it, and performs string containment checks for the listing root, a `Contents` entry, metadata extension nodes, tag extension text, and internal shard fields.

State and persistence behavior: Persistent state is the uploaded object body plus associated user metadata and tags. The test checks that metadata keys are returned in stripped form, meaning response XML uses `<project>` instead of an `x-amz-meta-project` style key. It also expects internal fields `<K>1</K>` and `<M>0</M>`, tying the response to RustFS's internal object layout metadata for this test environment.

Dependencies and integration points: This file bypasses the AWS SDK list operation because the metadata extension is query-parameter-specific and needs raw signed HTTP. It integrates request signing, host header handling, RustFS authentication credentials from the environment, HTTP response handling, S3-compatible object creation, XML serialization, tag encoding, and the object metadata lookup path behind listing.

Risks: XML validation is string-based rather than parsed, so it is sensitive to tag spelling and escaping but not to structural ordering. The expected internal `<K>` and `<M>` values may be environment-specific and could require updates if erasure or storage layout defaults change. Because metadata tag names are used directly as XML element names, invalid XML-name metadata keys would need separate coverage. The test does not explicitly stop the server.

Test signals: Signals are status `200 OK`, response containing `<ListBucketResult`, `<Contents>`, `<UserMetadata>`, `<project>alpha</project>`, `<owner>ops</owner>`, escaped `<UserTags>env=test&amp;project=alpha</UserTags>`, `<Internal>`, `<K>1</K>`, and `<M>0</M>`.
