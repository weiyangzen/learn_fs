# sources/object-store/minio/cmd/object-api-input-checks.go

## Purpose
This file centralizes argument validation for object API operations before those calls reach storage implementations. It turns invalid bucket names, object names, prefixes, and multipart upload ID markers into typed object API errors.

## Important APIs, types, and functions
Simple wrappers `checkCopyObjArgs`, `checkGetObjArgs`, and `checkDelObjArgs` call `checkBucketAndObjectNames`. `checkBucketAndObjectNames` validates bucket names with `s3utils.CheckValidBucketNameStrict`, except for MinIO metadata buckets, then requires a non-empty valid object prefix. `checkListObjsArgs` validates bucket and prefix for listing. `checkListMultipartArgs` extends listing validation with upload ID marker checks: an upload ID marker cannot be paired with a key marker ending in `/`, and non-empty upload ID markers must decode as raw URL base64. `checkNewMultipartArgs`, `checkPutObjectPartArgs`, `checkListPartsArgs`, `checkCompleteMultipartArgs`, and `checkAbortMultipartArgs` delegate to `checkObjectArgs` or `checkMultipartObjectArgs`. `checkObjectArgs` uses stricter object-name validation, while `checkPutObjectArgs` allows valid object prefixes but still rejects empty names.

## Control flow
Validation proceeds from bucket to object/prefix to multipart-specific markers. The bucket checks intentionally happen before object/prefix checks in most functions, which controls which error callers observe when multiple inputs are invalid. Multipart object operations validate the upload ID's raw URL base64 shape before object validation.

## State and persistence behavior
This file has no persistent state and does not check actual bucket existence. It only validates syntactic and platform-sensitive constraints before object-layer methods perform stateful bucket/object lookups.

## Dependencies and integration points
It depends on `s3utils`, base64 raw URL decoding, runtime OS detection, string helpers, MinIO metadata-bucket recognition, object-name helpers from `object-api-utils.go`, and typed errors from `object-api-errors.go`. It is used by object-layer implementations and handlers to keep validation behavior consistent across get, put, copy, delete, list, and multipart operations.

## Risks and test signals
Risks include subtle differences between prefix and object validation, especially around empty strings and trailing slash directory markers. Windows-specific rejection of backslashes in `checkBucketAndObjectNames` and broader invalid characters in lower helpers can create platform-specific behavior. Multipart upload ID validation depends on raw URL base64 and intentionally rejects padded IDs. The listed test files provide indirect signals through expected `BucketNameInvalid`, `ObjectNameInvalid`, `MalformedUploadID`, and `InvalidUploadIDKeyCombination` outcomes.
