# sources/user-network-fs/rclone/backend/webdav/tus-errors.go

Purpose: sentinel errors and client error type for the WebDAV TUS upload path.

Important APIs: `ErrChunkSize`, `ErrNilLogger`, `ErrNilStore`, `ErrNilUpload`, `ErrLargeUpload`, `ErrVersionMismatch`, `ErrOffsetMismatch`, `ErrUploadNotFound`, `ErrResumeNotEnabled`, `ErrFingerprintNotSet`, and `ClientError`.

Control flow/state: static errors only; `ClientError.Error` formats HTTP status code.

Dependencies/integration: standard `errors` and `fmt`; used by `tus.go` and `tus-uploader.go`.

Risks/test signals: several errors are vestigial from fuller TUS-client concepts and are not active in current flow. No direct tests.
