# sources/user-network-fs/rclone/backend/storj/fs.go

## Purpose

`fs.go` implements rclone's Storj backend on top of `storj.io/uplink`. It handles access-grant configuration, bucket/object listing, uploads, bucket creation/removal, server-side move/copy, purge, and public links.

## Important APIs, Types, and Functions

`Options` stores access grant and optional satellite/API-key/passphrase inputs. `Fs` stores name, root, options, feature flags, parsed `uplink.Access`, and open `uplink.Project`. Key functions include registration config logic, `NewFs`, `connect`, `absolute`, `List`, `ListR`, `NewObject`, `Put`, internal `put`, `Mkdir`, `Rmdir`, `Move`, `Copy`, `Purge`, `PublicLink`, and `newPrefix`.

## Control Flow

Config can use an existing access grant or create one from satellite/API key/passphrase, saving the serialized grant. `NewFs` normalizes root to NFC, parses or requests access, opens a project, and validates file-root cases. Listings operate at project root by listing buckets, or inside a bucket by listing objects with a prefix; recursive listing sets `Recursive: true`. Uploads call `UploadObject`, set custom metadata `rclone:mtime`, copy the input, and commit. If bucket-not-found occurs during upload/commit, the bucket is ensured and a retry error is returned. Move/copy retry after ensuring destination bucket. Public links create a shared read-only access and register it through Storj Edge.

## State and Persistence Behavior

Runtime state is the open project and access. Persistent config may be updated with a serialized access grant. Remote state includes buckets, objects, custom metadata, and public edge credentials.

## Dependencies and Integration Points

It depends on rclone `bucket`, `config`, `fserrors`, Unicode normalization, `storj.io/uplink`, and `storj.io/uplink/edge`. It implements list recursive, put stream, move, copy, purge, and public link optional interfaces.

## Risks and Edge Cases

The file contains a duplicated unreachable `return f, fs.ErrorIsFile`. Bucket creation during upload intentionally returns a retry error, so callers must retry. Storj rate-limits repeated writes to the same key; commit maps `ErrTooManyRequests` to a retry after sleeping one second. Hashes are unsupported. Prefix-directory semantics are inferred from object listings, so empty subdirectories are not preserved below buckets.

## Test Signals

`storj_test.go` runs generic integration tests. Additional signals include access-grant creation and saving, root-as-file handling, bucket creation on first upload, recursive listing, server-side move/copy across buckets, purge behavior, and public link generation.
