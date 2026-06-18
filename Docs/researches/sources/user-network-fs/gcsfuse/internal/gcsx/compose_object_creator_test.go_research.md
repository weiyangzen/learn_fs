## sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator_test.go

Purpose: validates `composeObjectCreator` append behavior against a mocked GCS bucket.

Important APIs and fixtures: `ComposeObjectCreatorTest`, fake source/temp/composed objects, matchers for delete request names, and mock expectations for `CreateObject`, `ComposeObjects`, and `DeleteObject`. The suite uses the project’s jacobsa-style test harness rather than testify.

Control flow and behavior covered: constructor creation, temp object creation request wiring, creation error propagation, compose request construction, destination preconditions, source list ordering, mtime metadata injection, and cleanup. It specifically checks that object metadata and properties such as cache control, content disposition, encoding, content type, custom time, event hold, storage class, and custom metadata are preserved across compose.

State/persistence signals: tests assert that temp object deletion is attempted after compose, and that delete failures surface only after successful compose. They verify the intended remote transaction model: temp create, compose old+temp into destination, delete temp.

Dependencies/integration: depends on `mock_bucket`, `gcs` request/response types, `time`, and error type matching for `gcs.PreconditionError` and `gcs.NotFoundError`.

Risks/test signals: the suite gives strong confidence in request construction and error wrapping, but not in random name uniqueness or real GCS compose semantics. It documents that `NotFoundError` during compose is treated as a precondition error.
