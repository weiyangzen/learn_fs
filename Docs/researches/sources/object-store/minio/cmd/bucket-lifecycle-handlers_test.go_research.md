# Research: sources/object-store/minio/cmd/bucket-lifecycle-handlers_test.go

Purpose: tests S3 bucket lifecycle HTTP endpoints for authentication failures and the core PUT/GET/DELETE lifecycle.

Important APIs and helpers: `TestBucketLifecycleWrongCredentials` and `TestBucketLifecycle` invoke `ExecObjectLayerAPITest` with lifecycle endpoints. Helpers `testBucketLifecycleHandlersWrongCredentials`, `testBucketLifecycleHandlers`, and `testBucketLifecycle` build signed V4 requests with `newTestSignedRequestV4`, route through `apiRouter`, and compare status, XML response bodies, and unmarshaled `APIErrorResponse` fields.

Control flow: the wrong-credential test matrix sends GET, PUT, and DELETE using empty credentials and invalid credentials, expecting `AccessDenied` or `InvalidAccessKeyId`. The happy-path matrix first sends invalid lifecycle XML cases to assert `InvalidArgument`, then successfully PUTs a lifecycle rule, GETs the canonical XML, DELETEs it, and finally confirms subsequent GET returns `NoSuchLifecycleConfiguration`.

State and persistence behavior: the ordered test intentionally relies on lifecycle config persisted by the PUT being visible to GET and removed by DELETE. It validates the handler path through `globalBucketMetadataSys.Update` and `Delete` at a behavioral level.

Dependencies and integration points: depends on the shared object-layer test harness, HTTP router, request signing utilities, XML error unmarshalling, and lifecycle handler endpoint registration.

Risks: the success test is order-dependent, so running individual cases independently would not be meaningful. It asserts exact lifecycle XML bytes for the GET response, making it sensitive to marshaling order or namespace changes. It only uses V4 signing and does not test V2 signing.

Test signals: strong signals for auth rejection, invalid XML validation, persistence across PUT/GET, deletion, and S3 error body shape. Missing signals include Content-MD5 enforcement, object-lock lifecycle validation, transition tier validation in the handler path, and MinIO-specific updated-at header handling.
