# sources/user-network-fs/rclone/backend/googlecloudstorage/googlecloudstorage.go

## Purpose
This file implements the rclone backend for Google Cloud Storage, not Google Drive. It registers the `gcs` prefixed remote, handles OAuth/service-account/environment/anonymous access, maps rclone paths to GCS buckets and object names, and implements bucket listing/creation/removal, object listing, upload, download, copy, metadata-based mtimes, and optional directory marker objects.

## Important APIs, Types, And Control Flow
The key types are `Options`, `Fs`, and `Object`. `NewFs` fills default ACLs, loads service-account credentials from JSON content or a shell-expanded file, selects authentication mode, initializes a Google Storage service with optional endpoint override, sets feature flags, and checks whether a bucket/path root is actually an object. `setRoot` and `split` manage bucket/path decomposition and encoder translation.

Listing is handled by `list`, `listDir`, `listBuckets`, `ListP`, and `ListR`. `list` wraps `Objects.List`, applies prefixes and delimiters, emits synthetic directories from `Prefixes`, treats trailing slash objects as directory markers, maps not-found to `fs.ErrorDirNotFound`, and checks marker existence for empty directories when `directory_markers` is enabled. `ListP` uses `list.WithListP`; root-level listings require `project_number`.

Writes and bucket lifecycle are handled by `Mkdir`, `mkdirParent`, `makeBucket`, `checkBucket`, `createDirectoryMarker`, `Put`, `PutStream`, and `Object.Update`. Uploads create parent buckets/directories unless writing a marker, attach mime type and mtime metadata, honor selected upload headers, storage class, object ACLs, and requester-pays user project. `Rmdir` removes directory markers or buckets depending on path depth. `Copy` uses GCS rewrite, handling multi-call rewrite tokens.

Object metadata uses `setMetaData`, `readObjectInfo`, `readMetaData`, `metadataFromModTime`, and `SetModTime`. Mtime is read from rclone `mtime`, then gsutil's `goog-reserved-file-mtime`, then GCS `Updated`. `SetModTime` copies the object to itself with updated metadata to avoid requiring PATCH permissions. `Open` downloads via the object's media link, supports range options, requester-pays query parameter, and gzip handling.

## State And Persistence
Runtime state includes authenticated HTTP client, storage service, bucket cache, pacer, root bucket/directory, and a one-time compressed-object warning. Remote persistent state includes buckets, objects, metadata, ACL/IAM policy choices, storage class, and optional slash-suffixed marker objects for empty directories. Local persistence is limited to OAuth token/config mechanisms managed by rclone.

## Dependencies And Integration Points
The backend integrates with `google.golang.org/api/storage/v1`, `googleapi`, `oauthutil`, `bucket.Cache`, rclone `list`, `fshttp`, `pacer.NewS3`, `encoder`, and requester-pays `user_project`. It implements `fs.Copier`, `fs.PutStreamer`, `fs.ListRer`, `fs.ListPer`, and object `MimeTyper`; MD5 is decoded from GCS base64 metadata.

## Risks And Test Signals
Risks include the deprecated storage API client, endpoint subpath limitations for uploads, service-account role limitations around bucket checks, directory marker edge cases with double slashes, gzip objects whose size/hash become unknown when decompressed, ACL behavior with bucket policy only, requester-pays propagation, and metadata update via self-copy. Tests should cover authenticated modes, bucket root and object root, directory markers, gzip downloads, range reads, storage-class headers, requester-pays, and rewrite continuation.
