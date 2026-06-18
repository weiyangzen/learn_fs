# sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper.go

## Purpose
This file provides a helper for constructing `CreateObjectRequest` values used when creating or overwriting objects while preserving source metadata and setting gcsfuse mtime metadata.

## Important APIs and Control Flow
`MtimeMetadataKey` is `gcsfuse_mtime`, written by sync flows as an RFC3339Nano UTC timestamp. `NewCreateObjectRequest` accepts an optional source `Object`, destination object name, optional mtime, and chunk retry/transfer timeouts. With nil source object, it creates a request for `objectName` with generation precondition zero and an empty metadata map. With a source object, it copies source metadata and object attributes, sets generation and metageneration preconditions from the source, and uses `srcObject.Name` as the request name. If `mtime` is non-nil, it overwrites or inserts `gcsfuse_mtime`.

## State, Dependencies, and Integration
There is no persistent state. The function allocates a fresh metadata map and uses `maps.Copy` to avoid aliasing source metadata. Dependencies are `maps` and `time`. It integrates with sync/write paths that need safe preconditioned object recreation.

## Risks and Test Signals
When `srcObject` is non-nil, `objectName` is ignored and `srcObject.Name` is used. That is likely intentional for overwrite/rewrite flows but can surprise callers expecting rename behavior. Only selected attributes are copied; ACL and content language are not all necessarily carried unless included. Tests cover nil source, existing source, nil mtime, metadata copying, and timeout propagation.
