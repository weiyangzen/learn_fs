# sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3Server.cpp

## Purpose
Implements a deterministic mock S3 HTTP server for FoundationDB simulation and ctests, supporting object CRUD, bucket operations, list operations, tagging, multipart upload, optional persistence, and direct request processing for chaos wrappers.

## Important APIs, Types, And Functions
`MockS3GlobalStorage` stores buckets, objects, multipart uploads, persistence directory, and load/enabled flags. `ObjectData` stores content, headers, tags, ETag, and last-modified timestamp. `MultipartUpload` stores upload ID, target bucket/object, parts, metadata, and initiation time. Persistence helpers include `atomicWriteFile()`, `readFileContent()`, `deletePersistedFile()`, JSON serializers/deserializers, `persistObject()`, `persistMultipartState()`, `deletePersistedObject()`, `deletePersistedMultipart()`, `loadPersistedObjects()`, and `loadPersistedMultipartUploads()`. `MockS3ServerImpl` routes requests through handlers for multipart, tags, list, bucket, and object operations. Public entry points include `processMockS3Request()`, `startMockS3Server()`, `startMockS3ServerReal()`, `clearMockS3Storage()`, `enableMockS3Persistence()`, `loadMockS3PersistedStateFuture()`, `initializeMockS3Persistence()`, and `registerMockS3Server()`.

## Control Flow
Incoming requests are logged, parsed into bucket/object/query parameters, and routed by query keys and HTTP verb. Multipart start returns an existing upload ID for the same object when present or creates and persists a new upload. Upload-part stores part content by part number and persists multipart state. Complete concatenates parts in key order, creates the final object, persists it, deletes upload state, and returns XML. Object `PUT`, `GET`, `DELETE`, and `HEAD` update/read global storage and response headers. List builds XML pages from sorted object names using prefix, marker/continuation token, and max-keys. Simulation registration enables persistence, loads prior state, and registers an HTTP handler once per address.

## State And Persistence Behavior
All mock S3 data is in a function-local static `MockS3GlobalStorage`, intentionally shared across simulated processes. Persistence writes objects under `<dir>/objects/<bucket>/<object>.data` plus `.meta.json`, and multipart state under `<dir>/multipart/<uploadId>.state.json` plus per-part files and metadata. Atomic writes use unique nondeterministic temp paths and `OPEN_ATOMIC_WRITE_AND_CREATE`; deletes are durable and best-effort. Loading sorts directory listings for deterministic replay. `clearMockS3Storage()` clears in-memory buckets/uploads but not the server registry.

## Dependencies And Integration Points
Depends on `fdbrpc/HTTP`, simulator HTTP registration, Flow trace/random/async-file/platform utilities, and RapidJSON. `processMockS3Request()` is used by `MockS3ServerChaos.cpp` to wrap normal processing. The server backs S3 blob-store tests and workloads that need deterministic S3 semantics inside FoundationDB simulation or standalone ctest HTTP mode.

## Risks And Edge Cases
The implementation is intentionally simplified and not a full S3 clone. XML parsing for tags is regex-based. Path components are not URL-decoded, but query values are. Range requests support `bytes=start-end` and open-ended ranges, but suffix byte ranges are not supported. `handleGetObject()` clamps ranges to `content.size() - 1`, which is delicate for empty content. Persistence skip-if-exists behavior avoids duplicate concurrent writes but can conflict with true last-writer-wins overwrite expectations. Multipart completion trusts stored parts and ignores the client completion XML part list. Registry state must stay aligned with simulator HTTP handlers to avoid duplicate registration assertions.

## Test Signals
Inline unit tests cover request parsing and range-header parsing. Build target `fdbserver_mocks3_test` exercises these tests. Integration signals include S3 blob-store workload success, persistence load/restore trace events, correct ETag/MD5 headers, multipart final object size, and real HTTP ctest startup.
