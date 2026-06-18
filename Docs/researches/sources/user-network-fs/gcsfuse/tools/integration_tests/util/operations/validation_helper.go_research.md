# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/validation_helper.go

Purpose: shared validation and retry helpers for integration tests.

Important APIs/types/functions: `ValidateNoFileOrDirError`, `ValidateObjectNotFoundErr`, `ValidateESTALEError`, `ValidateEIOError`, `CheckErrorForReadOnlyFileSystem`, `SkipKLCTestForUnsupportedKernelVersion`, and generic `RetryUntil[T]`.

Control flow: validators assert expected filesystem, syscall, read-only, and GCS not-found errors. `RetryUntil` loops until an operation returns nil error or a context deadline expires, logging attempts and failing the test on timeout.

State/persistence behavior: reads filesystem and GCS state but does not write it. `RetryUntil` creates a deadline context and ticker.

Dependencies/integration: integrates with internal `common`, `gcs`, `storageutil`, syscall errors, and `testify`.

Risks/test signals: error matching uses string/regexp checks around platform text, so behavior can vary by OS or wrapped error wording. `RetryUntil` fatal-exits tests rather than returning the last error.
