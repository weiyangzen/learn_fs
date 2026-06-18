# sources/user-network-fs/rclone/backend/webdav/tus.go

Purpose: connects WebDAV object updates to the TUS resumable upload protocol for ownCloud Infinite Scale.

Important APIs: `Object.updateViaTus`, `Fs.getTusLocationOrRetry`, and `Object.CreateUploader`.

Control flow/state: builds metadata from filename, mtime, and content type; creates an `Upload`; POSTs to the parent directory with `Upload-Length`, `Upload-Metadata`, and `Tus-Resumable`; consumes HTTP 201 Location; then uploads chunks from offset zero. Resume/fingerprint storage is not implemented.

Dependencies/integration: `context`, `fmt`, `io`, `net/http`, `filepath`, `strconv`, rclone `fs`, `rest`; selected by `Object.Update` when `canTus` is set by Infinite Scale quirks.

Risks/test signals: `getTusLocationOrRetry` assumes a response object; no persistent resume support. Coverage depends on Infinite Scale integration tests.
