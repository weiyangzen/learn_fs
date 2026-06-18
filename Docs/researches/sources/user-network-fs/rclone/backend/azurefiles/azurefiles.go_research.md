# Research: sources/user-network-fs/rclone/backend/azurefiles/azurefiles.go

## Purpose
This file implements rclone's Microsoft Azure Files backend on supported platforms. It maps rclone filesystem operations onto Azure File Share APIs for a configured share, including directory creation/removal, listing, uploads with preallocated size, server-side copy/move, random-access writes, MIME/MD5/modtime properties, and quota reporting.

## Important APIs, Types, and Functions
- `Options` embeds shared Azure auth options and adds `share_name`, `chunk_size`, `max_stream_size`, `upload_concurrency`, and encoding.
- `Fs` stores backend name/root/options, feature flags, a share client, and the root directory client.
- `Object` stores remote, size, MD5 bytes, modtime, and content type.
- `newFsFromOptions` builds the Azure Files service client through the shared auth helper, sets `FileRequestIntent=backup` for token credentials, binds to the configured share/root directory, advertises features, and detects file roots.
- `NewFs` parses config and delegates to `newFsFromOptions`.
- Path helpers `absPath`, `dirClient`, and `fileClient` encode rclone paths under `root`.
- Directory and listing methods include `absMkdir`, `Mkdir`, `mkParentDir`, `Rmdir`, `List`, and `ListP`.
- Object methods include `NewObject`, `setMetadata`, `getMetadata`, `Hash`, `MimeType`, `ModTime`, `SetModTime`, `Open`, `Update`, and `Remove`.
- Server-side operations are `Move`, `DirMove`, and `Copy`.
- Random write support is implemented by `writerAt`, `WriteAt`, `Close`, and `OpenWriterAt`.
- `About` returns share usage from `GetStatistics`.

## Control Flow
Initialization constructs a generic Azure service client using shared auth callbacks, then obtains a share client and root directory client for `ShareName`. `NewFs` also probes whether the configured root points to a file; if so it rewrites root to the parent and returns `fs.ErrorIsFile`.

Listing checks directory existence with `GetProperties`, pages `ListFilesAndDirectories`, converts directories to `fs.Dir` entries with LastWriteTime/ID/size when present, and converts files to `Object` entries with size and modtime from listing properties.

Uploads call `Update`. If size is unknown, the file is temporarily created at `max_stream_size` and the stream is counted; otherwise the known size is used. New files create parent directories and call `Create`; existing files are resized if needed. The data is sent through `UploadStream` with configured chunk size/concurrency. MD5 comes from source hash if available or is calculated via `io.TeeReader`. After upload, `SetHTTPHeaders` sets final content length, SMB LastWriteTime, MD5, content type, and supported content headers, truncating unknown-size uploads to actual bytes.

Reads honor range and seek options with `DownloadStream`. Server-side `Move` and `DirMove` use Azure rename APIs with parent creation and destination existence checks. `Copy` calls `StartCopyFromURL`, polls while pending, and returns the new object. `OpenWriterAt` creates/truncates a file and `WriteAt` resizes as needed under a mutex before uploading byte ranges.

## State and Persistence
Persistent remote state includes shares, directories, files, file sizes, content, SMB LastWriteTime, content headers, and Content-MD5. Unknown-size uploads may temporarily reserve up to `max_stream_size` bytes. Local state is minimal: object metadata caches, feature flags, and writerAt size protected by a mutex. There is no pacer/retry layer in this file despite a TODO noting it.

## Dependencies and Integration Points
The backend depends on Azure `azfile` service/share/directory/file clients, file error helpers, the shared Azure auth package, rclone `fs` optional interfaces, config parsing, path encoders, list helper, hash support, and counting readers. It advertises `PutStreamer`, `Abouter`, `Mover`, `DirMover`, `Copier`, `OpenWriterAter`, `ListPer`, and MIME support.

## Risks and Edge Cases
- `share_name` is documented as required but `newFsFromOptions` does not explicitly validate non-empty input before creating a share client.
- Unknown-size uploads can consume `max_stream_size` quota temporarily; interruption before final `SetHTTPHeaders` may leave an oversized partial file.
- There is no backend pacer/retry wrapper, so transient Azure failures surface directly.
- The TODO block notes incomplete metadata support and HTTP header gaps; only selected headers from open options are written.
- `SetModTime` preserves current MD5/content type values, but if they were not loaded it may set nil/empty properties.
- `ModTime` returns `time.Now()` when unknown, which can destabilize comparisons for objects created from sparse listing data without LastWriteTime.
- `Copy` uses the source file URL directly; cross-auth/cross-account scenarios are constrained by what the URL permits.
- `writerAt.Close` does not set MD5, modtime, or content type after random writes.

## Test Signals
`azurefiles_test.go` runs generic fstests against `TestAzureFiles:`. `azurefiles_internal_test.go` defines a skipped auth matrix for connection string, account/key, and SAS URL construction. There are no focused tests in this group for unknown-size upload truncation, random writes, copy/move edge cases, or header preservation.
