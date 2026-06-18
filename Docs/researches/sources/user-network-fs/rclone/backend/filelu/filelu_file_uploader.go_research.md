# sources/user-network-fs/rclone/backend/filelu/filelu_file_uploader.go

Purpose: This file implements FileLu upload paths: fixed-size multipart uploads for large objects, upload-part requests, simple form upload through an upload server, and upload-server discovery.

Important APIs and types: Functions include `multipartUpload`, `uploadPart`, `uploadFile`, `getUploadServer`, `uploadFileWithDestination`, and `respBodyClose`.

Control flow: `multipartUpload` ensures the parent directory, initializes multipart upload, buffers input up to configured chunk size using 1 MiB reads, uploads each part with numbered PUT requests, uploads a final partial part, then completes the multipart upload. `uploadFile` ensures the target directory exists, lists existing entries and deletes an existing file with the same remote, gets an upload server/session, and posts a multipart form containing session ID, account type, folder path, and file content. `uploadFileWithDestination` streams multipart data through an `io.Pipe` from a goroutine while the HTTP request is sent and decodes an array response for `file_code` and `file_status`.

State and persistence behavior: Upload state is held in provider session IDs and multipart upload IDs. Local transient state includes chunk buffers, a pipe, multipart writer, and a boolean used to decide whether to attempt cleanup after copy failure. Server-side state may include deletion of an existing destination before upload completion.

Dependencies and integration points: Called by `Object.Update` and `Fs.Move`. It uses raw `net/http` for upload servers and `rest` for upload-server discovery. It relies on encoding helpers and FileLu API conventions.

Risks: `multipartUpload` appends to a buffer and uploads the whole buffer when length is at least chunk size, so reads larger than `chunk_size` could produce oversized parts. The simple upload path deletes existing files before upload, creating a data-loss window. `uploadFileWithDestination` references `result[0].FileStatus` even when `len(result) == 0`, which can panic on empty responses. The `isDeletionRequired` flag is written from a goroutine without synchronization. Retry around a streaming `io.Pipe` request is fragile because the body cannot be replayed.

Test signals: No direct tests cover upload edge cases; integration tests are the main signal for normal-size uploads.
