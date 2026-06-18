# sources/object-store/minio/cmd/kms-handlers.go

## Purpose

`kms-handlers.go` implements MinIO's `/minio/kms/v1` admin-style HTTP handlers for status, metrics, API discovery, version, key creation, key listing, and key health checks. These handlers bridge authenticated admin requests to `GlobalKMS`, converting KMS responses and errors into JSON API responses while auditing every request.

## Important APIs, Control Flow, And State

The handler methods live on `kmsAPIHandlers`. `KMSStatusHandler`, `KMSMetricsHandler`, `KMSAPIsHandler`, and `KMSVersionHandler` validate the request with the corresponding `policy.KMS*Action`, reject uninitialized `GlobalKMS` with `ErrKMSNotConfigured`, call the KMS method, marshal the response, and write JSON. `KMSCreateKeyHandler` additionally extracts `key-id`, revalidates the signature, and calls `checkKMSActionAllowed` against the specific key name before `GlobalKMS.CreateKey`. `KMSListKeysHandler` asks the KMS for the requested pattern and then filters the returned key names in place through resource-specific IAM checks. `KMSKeyStatusHandler` defaults an empty `key-id` to `GlobalKMS.DefaultKey`, authorizes the concrete key, generates a test data key, decrypts it with the same associated data, and constant-time compares plaintexts to populate `madmin.KMSKeyStatus`.

Persistent state is in the external or stub KMS, not in this file. Dependencies include `GlobalKMS`, `validateAdminReq`, `validateAdminSignature`, `globalIAMSys`, MinIO API error helpers, `madmin-go`, internal `kms`, and MinIO policy types. The notable integration detail is the resource overload: `checkKMSActionAllowed` passes the KMS key name as `BucketName` because the shared policy engine builds resources from that field.

## Risks And Test Signals

Risks are subtle authorization regressions: broad admin validation is not enough for key-specific create/list/status, and list filtering must preserve order while removing unauthorized keys. Key status intentionally returns HTTP success with `EncryptionErr` or `DecryptionErr` fields for failed KMS operations after authorization. `kms-handlers_test.go` covers root/user access, resource-matching policies, no-resource legacy behavior, not-configured KMS, invalid credentials, and parity/differences with legacy admin KMS endpoints.
