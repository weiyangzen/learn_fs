# sources/user-network-fs/rclone/backend/seafile/object.go

## Purpose
This file implements the Seafile backend's `Object`, representing a file in a Seafile library. It supplies rclone object identity, size/modtime, open/download, upload/update, delete, and ID behavior.

## Important APIs, Types, And Functions
`Object` stores its parent `*Fs`, Seafile object ID, remote path, path within the library, size, modification time, and library ID. It implements `String`, `Remote`, `ModTime`, `Size`, `Fs`, `Hash`, `Storable`, `SetModTime`, `Open`, `Update`, `Remove`, and `ID`.

`Open` obtains a temporary download link with `o.fs.getDownloadLink` and streams data through `o.fs.download` with the object size and requested open options. `Update` obtains an upload link with `o.fs.getUploadLink`, calls `o.fs.upload`, retries up to three additional times on `ErrorInternalDuringUpload`, and updates the object's `size` and `id` from the upload response. `Remove` delegates to `o.fs.deleteFile`.

## Control Flow
Read flow is link acquisition followed by download. Write flow loops from retry 0 through 3, reacquiring a fresh upload link each time because Seafile upload links are single-use. Only the specific `ErrorInternalDuringUpload` error is retried; all other upload or link errors return immediately. Successful upload mutates local object fields and returns.

## State And Persistence Behavior
Remote state is the file content and metadata in Seafile. Local object state caches ID, size, modtime, library ID, and path. `SetModTime` returns `fs.ErrorCantSetModTime`, so mtime is read-only from this object implementation. Hashes are unsupported and return `hash.ErrUnsupported`.

## Dependencies And Integration Points
The file integrates with the parent Seafile `Fs` API helpers for download links, upload links, upload, and deletion. It implements rclone `fs.DirEntry`, `fs.ObjectInfo`, `fs.Object`, and optional `fs.IDer` behavior. It depends on rclone `fs`, `hash`, contexts, IO, and time.

## Risks And Edge Cases
The retry loop reuses the same `io.Reader` after a failed upload. If `o.fs.upload` consumes bytes before returning `ErrorInternalDuringUpload`, a retry with the same non-seeked reader may upload truncated or empty content unless the upload helper buffers or rewinds elsewhere. Unknown-size upload handling is not explicit in this file despite the comment; correctness depends on `o.fs.upload`. Modtime is not updated after successful upload, only size and ID are. Download and upload links are temporary, so operations are sensitive to expiration and single-use semantics.

## Test Signals
No direct tests for `Object` are in this subset. Expected coverage would come from Seafile backend integration tests for read, write, delete, ID, unsupported hashes, and the temporary 500 retry behavior.
