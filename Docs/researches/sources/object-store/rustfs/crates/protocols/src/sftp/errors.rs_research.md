# sources/object-store/rustfs/crates/protocols/src/sftp/errors.rs

## Purpose
`errors.rs` defines the SFTP error wrapper and common conversions from RustFS/S3/IAM failures into SFTPv3 status codes. It keeps client-visible responses limited to protocol status codes while logging backend details for operators.

## Important APIs, Types, and Functions
`SftpError(StatusCode)` converts into `StatusCode` and `StatusReply`. `ok_status(id)` builds successful `Status` payloads. `s3_error_to_sftp(op, err)` maps typed backend errors to `NoSuchFile`, `PermissionDenied`, or generic `Failure`. `auth_err` and `auth_err_unreachable` encode policy denial and IAM unavailability. `is_not_found_error` and `is_no_such_upload_error` expose the same classifier for control flow.

Internally, `BackendErrorKind`, `classify_s3_code`, and `classify_backend_error` avoid display-string parsing. `S3Error` is classified by `S3ErrorCode` and known canonical strings; under tests, `DummyError` gets equivalent classification.

## Control Flow
Callers pass backend failures into `s3_error_to_sftp`; the helper classifies, logs the display string, and returns an `SftpError`. Predicate helpers use the same classification path, so driver branches and wire mapping cannot drift independently.

## State and Persistence Behavior
The file is stateless. Its important persistence behavior is semantic consistency: one typed classifier feeds both response mapping and branch decisions.

## Dependencies and Integration Points
It depends on SFTP reply types, `s3s::S3Error`, error-code constants, and tracing. It is used by driver, read, write, directory, and multipart cleanup paths.

## Risks and Test Signals
The main risk is misclassification. Tests pin code-based behavior, verify unknown display strings do not map by substring, confirm not-found and access-denied handling, verify `ok_status`, and check `NoSuchUpload` for S3 and dummy errors.
