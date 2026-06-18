# sources/user-network-fs/rclone/backend/storj/object.go

## Purpose

`object.go` implements rclone object behavior for Storj objects, including remote path derivation, metadata-backed modtime, range reads, updates, and deletion.

## Important APIs, Types, and Functions

`Object` stores parent `Fs`, absolute `bucket/key`, size, created time, and modified time. `newObjectFromUplink` translates `uplink.Object` metadata into an `Object`, preferring custom `rclone:mtime` over server created time. Methods implement `fs.Object`: `String`, `Remote`, `ModTime`, `Size`, `Fs`, `Hash`, `Storable`, `SetModTime`, `Open`, `Update`, and `Remove`.

## Control Flow

Object creation computes the absolute path by combining filesystem root and relative path, normalizing to NFC. `Remote` returns the full absolute path when the `Fs` root is empty, otherwise trims the root prefix and slash. `Open` converts rclone `RangeOption` or `SeekOption` into uplink `DownloadOptions` offset and length, rejecting unsupported mandatory options. `Update` delegates to `Fs.put` for the same remote path and replaces the receiver with the returned object on success. `Remove` splits `absolute` into bucket/key and calls `DeleteObject`.

## State and Persistence Behavior

Object metadata is cached in the struct. Remote persistence is handled by Storj object storage. `SetModTime` is unsupported after upload; modtime is stored at upload time as custom metadata.

## Dependencies and Integration Points

It depends on rclone `fs`, `hash`, `bucket`, Unicode normalization, and `uplink`. It is tightly coupled to `fs.go` for project access and upload/update behavior.

## Risks and Edge Cases

Suffix range handling uses negative offsets for `RangeOption` with only an end value, matching uplink semantics but requiring careful interpretation. Hashes and post-upload modtime changes are unsupported. Corrupt `rclone:mtime` metadata falls back silently to created time.

## Test Signals

Integration tests should cover range and seek reads, update replacing receiver metadata, delete behavior, root-relative path calculation for project-root and bucket-root remotes, and modtime round-tripping through custom metadata.
