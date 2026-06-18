# sources/user-network-fs/rclone/backend/swift/swift.go

## Purpose

`swift.go` implements rclone's OpenStack Swift backend, including authentication, container/bucket behavior, paginated and recursive listing, uploads, dynamic large object segment handling, server-side copy, purge, metadata modtime, MD5 hashes, quota reporting, and MIME type support.

## Important APIs, Types, and Functions

`SharedOptions` defines chunking, large-object, segment-location, and encoding options. `Options` covers OpenStack auth fields, env auth, storage URL/token overrides, application credentials, storage policy, listing workarounds, and upload behavior. `Fs` stores the Swift connection, root container/directory, bucket cache, pacer, config, and features. `Object` stores remote path, size, last modified, content type, MD5, and headers. Key functions include `swiftConnection`, `NewFsWithConnection`, `NewFs`, `listContainerRoot`, `ListP`, `ListR`, `About`, `makeContainer`, `Purge`, `Copy`, segmented-upload helpers, object metadata/hash/large-object detection, `Open`, `updateChunks`, `Update`, `Remove`, and `urlEncode`.

## Control Flow

Initialization parses options, authenticates or applies environment credentials, wraps storage URL/token overrides, validates chunk size, sets root fields, auto-selects segment storage mode, and detects root-as-file. Listing uses Swift `ObjectsWalk` with delimiter for non-recursive listing and filters hidden `.file-segments` when segments live inside the container. Upload creates the container, sets modtime metadata, then either performs a single `ObjectPut` or uploads segments and writes a DLO manifest. Existing large-object segments are removed after successful replacement unless container versioning is enabled. Copy handles normal objects with `ObjectCopy` and large objects by copying each segment then uploading a manifest. Remove deletes the manifest/object first, then bulk-deletes segments when appropriate.

## State and Persistence Behavior

Runtime state includes connection auth, bucket cache, root split, object headers, and pacer. Persistent remote state includes containers, objects, metadata headers, segment containers or `.file-segments` directory objects, storage policies, and container versioning. Config can source credentials from environment but is not written here.

## Dependencies and Integration Points

It depends on `github.com/ncw/swift/v2`, rclone `fs`, `list`, `operations`, `bucket`, `encoder`, `pacer`, `random`, `readers`, and `atexit`. It implements purge, put stream, copy, recursive and paginated listing, MIME type, and usage interfaces.

## Risks and Edge Cases

Large-object handling is complex: DLO/SLO detection requires HEAD requests unless disabled, and `NoLargeObjects` can make hashes/copy/remove wrong if large objects exist. Segment cleanup is skipped when `leave_parts_on_error` is true or container versioning is enabled. Provider quirks drive automatic segment-location selection. Retry-after handling sleeps for short 429 delays and returns delayed retry errors for long ones. Directory markers must be filtered to avoid duplicate directories.

## Test Signals

Internal tests cover `urlEncode` and retry-after behavior. Integration tests should cover env and explicit auth, listing pagination workarounds, root-as-file, single and segmented uploads, DLO copy/remove cleanup, storage policy on segment containers, purge including directory markers, MD5 behavior, MIME metadata, and versioned containers.
