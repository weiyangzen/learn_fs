<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping_test.go

Purpose: unit tests for key branches of `errno` error conversion.

Important APIs/types/functions: suite `ErrorMapping`; `TestWithErrorMapping`; tests for permission denied, already exists, not found, canceled, unauthenticated gRPC, unauthenticated HTTP `googleapi.Error`, and `FileClobberedError`.

Control flow: tests build `status.Error` values, wrap them through `apierror.FromError` when appropriate, pass errors to `errno`, and compare against expected `syscall` errno constants.

State and persistence behavior: stateless unit coverage; no filesystem or bucket state.

Dependencies and integration points: uses gRPC status/codes, google API error types, `apierror`, gcsfuse clobber error, and testify suite/assert.

Risks: coverage is representative but not exhaustive. String-matched cases, context cancellation, storage object-not-exist, existing errno preservation, and fallback EIO are not covered here.

Test signals: confirms important public mappings to `EACCES`, `EEXIST`, `ENOENT`, `EINTR`, and `ESTALE`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping_test.go -->
