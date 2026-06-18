# sources/user-network-fs/rclone/backend/webdav/tus-uploader.go

Purpose: chunk-by-chunk TUS uploader for ownCloud Infinite Scale.

Important APIs: `Uploader`, `NotifyUploadProgress`, `Upload`, `UploadChunk`, `uploadChunk`, `broadcastProgress`, `NewUploader`, and `Fs.shouldRetryChunk`.

Control flow/state: loops until offset reaches upload size, seeks the upload stream, reads one configured chunk, sends PATCH or POST override with TUS headers, updates offset from server `Upload-Offset`, and notifies subscribers.

Dependencies/integration: HTTP/url/io/bytes/strconv, rclone `fs`, `rest`. Created by `Object.CreateUploader`.

Risks/test signals: broadcaster goroutine and notify channel have no close path; chunk requests lack `GetBody` for low-level retries after body write. No dedicated unit tests here.
