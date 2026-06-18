# sources/user-network-fs/gcsfuse/internal/fs/inode/name.go

Purpose: defines the inode `Name` value object that translates between local filesystem names and GCS object names. It is a small immutable struct with `bucketName` and `objectName`; an empty `bucketName` means a single mounted bucket, while a non-empty bucket name represents multi-bucket mounting where local paths are prefixed with the bucket directory.

Important APIs: `NewRootName`, `NewDirName`, `NewFileName`, and `NewDescendantName` construct names for bucket roots, directory marker-style object names, files, and descendants. `IsBucketRoot`, `IsDir`, `IsFile`, `GcsObjectName`, `LocalName`, `String`, `IsDirectChildOf`, and `ParentName` provide interpretation and navigation. Directories are represented by empty object name for roots or by trailing slash for non-root directories; files are anything else. `NewDirName` and `NewFileName` panic on invalid child construction, such as adding children under files or using empty child names.

Control flow and state: the code is pure string manipulation with no external persistence. `IsDirectChildOf` first rejects cross-bucket and non-prefix cases, then strips the parent prefix and ensures the remaining path segment does not contain another slash after optional trailing slash removal. `ParentName` trims a trailing slash, locates the last slash, and returns either bucket root or the slash-terminated parent directory object name; bucket roots return an error.

Dependencies and integration: it depends only on `errors`, `fmt`, and `strings`, but it is foundational for inode creation, lookup, directory listing, recursive operations, and GCS object naming throughout `internal/fs/inode`.

Risks: invariants are convention-based. Calling `IsDir` with a malformed `Name{objectName:""}` is safe because bucket root is checked first, but hand-built `Name` values that omit trailing slashes for directories will be interpreted as files. `NewDescendantName` does not verify that the descendant name is actually under the ancestor; callers must enforce that relationship.

Test signals: `name_test.go` covers bucket-prefixed and unprefixed mounts, directory/file classification, local and GCS name formatting, direct-child relationships, map-key comparability, and parent resolution including root error behavior.
