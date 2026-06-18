# sources/object-store/minio/cmd/kms-handlers_test.go

## Purpose

`kms-handlers_test.go` is the behavioral test matrix for the `/minio/kms/v1` router and related admin KMS endpoints. It verifies authentication, IAM policy action matching, KMS key-resource filtering, response bodies, and fallback errors when KMS is absent or credentials are invalid.

## Important Tests And Control Flow

The file defines route constants for KMS and admin KMS paths plus `kmsTestCase`, which carries method, path, query, policy, root/user mode, expected status, expected key names, and response snippets. `TestKMSHandlersCreateKey` checks denied access without policy, allow without resources, allow with matching `arn:minio:kms` resource, and deny on nonmatching resources. `TestKMSHandlersKeyStatus` creates a key as root, checks root success, user denial, legacy no-resource success, matching resource success, and nonmatching resource denial. `TestKMSHandlersAPIs` covers version/apis/metrics/status and confirms their resource field is ignored once the action is allowed. `TestKMSHandlersListKeys` verifies root returns all keys, user policy can filter keys by resource, query `pattern` combines with IAM filtering, empty filtered lists are successful, and a deny statement still blocks the action for backward compatibility. `TestKMSHandlerAdminAPI` documents that old admin KMS actions ignore resources. `TestKMSHandlerNotConfiguredOrInvalidCreds` asserts `501` when `GlobalKMS` is nil and `403` for invalid user credentials once a KMS exists.

The helpers set up an erasure admin testbed, register the KMS router, install `kms.NewStub`, create signed V4 requests, create users, parse inline policy JSON, and attach/detach policies through `globalIAMSys`.

## Risks And Test Signals

The strongest signal is authorization coverage, especially the newer KMS resource semantics. Gaps remain around KMS backend runtime failures, malformed KMS JSON from non-stub providers, pagination/list continuation, concurrent policy mutation, and malformed query values. The tests use the stub backend, so they validate MinIO routing and IAM behavior rather than external KMS interoperability.
