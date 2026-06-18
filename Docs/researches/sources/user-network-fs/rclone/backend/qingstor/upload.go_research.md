# sources/user-network-fs/rclone/backend/qingstor/upload.go

## Purpose
QingStor upload helper: implements single and multipart upload machinery.

## Important APIs, Types, And Functions
Important surface: uploadInput, uploader, multiUploader, chunk, completedParts, newUploader, singlePartUpload, upload, nextReader, initiate, send, complete, abort.

## Control Flow
reads first chunk to choose single vs multipart, starts worker goroutines, uploads parts, computes MD5 over part buffers, sorts completed parts, completes or aborts on error

## State And Persistence
remote multipart upload session; local reader position, upload ID, parts, shared error, MD5 hash.

## Dependencies And Integration Points
QingStor SDK, rclone atexit/logging, sync/io/md5.

## Risks And Test Signals
Risks and useful test signals: memory use for non-seekable readers, ignored bucket-init errors, part numbering, checksum with concurrency.
