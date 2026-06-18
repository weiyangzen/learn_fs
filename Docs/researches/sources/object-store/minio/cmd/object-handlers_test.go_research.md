# sources/object-store/minio/cmd/object-handlers_test.go

## Purpose
This file is the broad HTTP/S3 compatibility test suite for MinIO object handlers. It drives registered API routes through `httptest` requests and verifies object data, XML error bodies, S3 status codes, auth behavior, anonymous-policy behavior, nil object-layer behavior, multipart flows, copy semantics, checksums, range reads, streaming SigV4 uploads, compression/encryption combinations, and V2/V4 signing parity.

## Important APIs, Types, and Functions
- `type Fault` plus constants `MissingContentLength`, `TooBigObject`, `TooBigDecodedLength`, `BadSignature`, `BadMD5`, and `MissingUploadID` model request mutations used across PUT and multipart tests.
- `TestAPIHeadObjectHandler`, `TestAPIGetObjectHandler`, `TestAPIPutObjectHandler`, `TestAPICopyObjectHandler`, `TestAPIDeleteObjectHandler`, and related helpers exercise single-object HTTP endpoints.
- `TestAPIGetObjectWithMPHandler` and `TestAPIGetObjectWithPartNumberHandler` validate ranged and part-number reads from single-part, multipart, encrypted, and compressed objects.
- Multipart HTTP tests cover `NewMultipart`, `PutObjectPart`, `CopyObjectPart`, `CompleteMultipart`, `AbortMultipart`, and `ListObjectParts` handlers, including presigned list requests.
- The file depends heavily on shared test harnesses such as `ExecObjectLayerAPITest`, `ExecExtendedObjectLayerAPITest`, `ExecObjectLayerAPIAnonTest`, `ExecObjectLayerAPINilTest`, request builders, signing helpers, `uploadTestObject`, `NewDummyDataGen`, and direct `ObjectLayer` methods for setup/verification.

## Control Flow
Each public `Test...` wrapper initializes the object-layer API harness with endpoint names. The paired `test...` helper usually creates prerequisite objects or multipart upload IDs, constructs signed HTTP requests, serves them through `apiRouter`, checks status codes and response bodies, then verifies persistence by reading back through `ObjectLayer`. Most major handlers are checked twice with SigV4 and SigV2 where applicable. Anonymous calls are routed through policy helper tests, while nil-object-layer requests verify early server-not-initialized behavior.

GET and HEAD tests first upload deterministic data, then check normal responses, missing objects, invalid object names, invalid credentials, byte ranges, and encrypted HEAD behavior requiring SSE-C headers. PUT tests mutate content length, MD5, storage class, checksums, copy-source headers, and streaming chunk signatures. Copy tests validate metadata directives, source condition headers, version ID parsing, same-source restrictions, copy-part range validation, and object data preservation. Multipart completion tests build real parts, marshal `CompleteMultipartUpload` XML, and assert ETag/order/part-size/upload-ID failures before a success path.

## State and Persistence Behavior
The tests mutate in-memory or disk-backed test object layers by creating buckets, objects, multipart upload state, uploaded parts, copied objects, and deleted objects. They assert persisted data by calling `GetObjectNInfo`, `GetObjectInfo`, `ListObjectParts`, or direct object reads after handler execution. Extended runs repeatedly execute the same behavior under compression, encryption, and versioning configurations, so state expectations include plaintext length preservation, encrypted-object header requirements, compression metadata presence, multipart ETag formation, and deletion idempotence.

## Dependencies and Integration Points
The file integrates HTTP routing, S3 request signing, XML request/response encoding, bucket policy helpers, MinIO object layer APIs, encryption/compression globals, checksum hashing, multipart metadata, and test data generators. It is a consumer-side validation layer for handlers implemented in object handler files, including `object-multipart-handlers.go`. It also uses package globals such as `globalPolicySys`, `globalIsTLS`, `globalMaxObjectSize`, and compression state, so tests depend on correct setup/teardown discipline.

## Risks and Edge Cases
- Global state such as policy, TLS, compression, encryption, and KMS must be reset carefully or later subtests can inherit unexpected behavior.
- Some branches use direct object-layer calls for setup while only one handler is registered, so failures can reflect setup assumptions as well as handler behavior.
- Large dummy data and extended matrix tests can be expensive; `testing.Short()` reduces some multipart GET cases.
- There is a suspicious switch in copy-part test request creation: `case !testCase.invalidPartNumber || !testCase.maximumPartNumber` is true for most combinations, which can make the invalid/max part-number branches unreachable.
- Error assertions are highly S3-compatibility-sensitive, so changes in API error mapping, resource path normalization, or header casing can break tests.

## Test Signals
This file is itself the signal source. It covers success and failure statuses, XML API error codes, response content equality, checksum headers, ETag headers, anonymous policy authorization, V2/V4 signatures, presigned requests, streaming-chunk signature faults, encrypted HEAD/GET behavior, compression persistence, multipart upload lifecycle, and nil backend handling.
