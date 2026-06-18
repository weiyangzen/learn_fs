## sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket_test.go

Purpose: table-driven tests for content-type inference across all creation paths wrapped by `contentTypeBucket`.

Important APIs and fixtures: `contentTypeBucketTestCases` enumerates object names, initially supplied content types, and expected final values. Tests exercise `CreateObject`, `CreateObjectChunkWriter`, `CreateAppendableObjectWriter`, and `ComposeObjects`.

Control flow and behavior covered: each test creates a fake bucket wrapper, sends requests through `NewContentTypeBucket`, and checks the returned object or captured writer request content type. `ComposeObjects` first creates source objects and then composes into a destination to validate destination-name extension inference.

State/persistence signals: confirms the wrapper influences request metadata before storage persists it and does not override an explicit caller-supplied content type. It also covers empty or unknown extensions by expecting the standard library’s extension mapping result.

Dependencies/integration: uses fake storage bucket behavior from internal storage test utilities and the public `gcs` request types.

Risks/test signals: tests cover the wrapper surface broadly, but they are only as complete as Go’s MIME database in the running environment. They do not verify wrapper ordering with other bucket decorators.
