# sources/user-network-fs/rclone/backend/webdav/tus-upload.go

Purpose: in-memory upload model for TUS uploads.

Important APIs: `Metadata`, `Upload`, `NewUpload`, `EncodedMetadata`, `Progress`, `Offset`, `Size`, `Finished`, and `updateProgress`.

Control flow/state: non-seekable readers are fully buffered into memory to provide `io.ReadSeeker`; metadata values are base64-encoded for the TUS `Upload-Metadata` header; offset tracks upload progress.

Dependencies/integration: `bytes`, `encoding/base64`, `fmt`, `io`, `strings`. Used by `updateViaTus` and `Uploader`.

Risks/test signals: large non-seekable uploads can consume large memory; `Progress` divides by size. Metadata header order is nondeterministic but should be protocol-safe.
