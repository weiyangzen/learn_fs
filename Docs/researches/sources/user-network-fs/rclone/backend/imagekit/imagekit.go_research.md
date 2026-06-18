# sources/user-network-fs/rclone/backend/imagekit/imagekit.go

## Purpose
Implements rclone's ImageKit.io media-library backend, adapting ImageKit file/folder APIs to filesystem listing, object access, upload, deletion, metadata, and public links.

## Important APIs, Types, and Functions
`Options` defines endpoint, public/private keys, signed URL preference, version listing, and encoder. `Fs` stores root, options, ImageKit client, pacer, and features. `Object` stores remote path, ImageKit file path, MIME type, timestamp, full `client.File`, and optional version ID.

Major methods are `NewFs`, `List`, `newObject`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `PublicLink`, `Object.Open`, `Object.Update`, `Object.Remove`, `Object.Metadata`, and `uploadFile`.

## Control Flow
`NewFs` parses config, creates the client, sets root to an absolute slash-prefixed path, fills features, and probes whether the root names an existing file by searching the parent folder and filename. `List` verifies non-root directories by querying folder existence, then fetches folders and files using paged helper methods. Folders are converted to `fs.Dir`; files are converted to `Object`, with old versions exposed through `version.Add`.

`NewObject` checks whether the target is a folder first, then searches a file by parent path and encoded filename. `Put` rejects zero-byte uploads and delegates to `uploadFile`. Object reads generate a delivery URL with `tr=orig-true` and `updatedAt` cache-busting, set a Range header, and compensate by discarding bytes locally if the server ignores range requests and returns 200. Updates upload with the existing privacy setting; new uploads use `OnlySigned` as `IsPrivateFile`. Metadata maps ImageKit system fields, embedded metadata, tags, coordinates, privacy, and AI tag sources into rclone metadata.

## State and Persistence
Remote state is the ImageKit media library. Local backend state is config/options, the client, and object snapshots from `client.File`. No dircache is used; each list/object lookup queries ImageKit. `Rmdir` checks emptiness via `List` before deleting; `Purge` deletes folders without listing children.

## Dependencies and Integration Points
Depends on the local ImageKit client package, rclone `fs`, `configstruct`, `hash`, `encoder`, `pacer`, `readers`, and `version`. It exposes rclone features including `ReadMimeType`, `ReadMetadata`, `FilterAware`, and `PublicLinker`.

## Risks and Edge Cases
`Rmdir` and `Purge` dereference `res.StatusCode` without checking whether `res` is nil after `DeleteFolder`. `Object.Open` creates a plain `http.Client{}` instead of using rclone's configured HTTP client, so proxy/TLS/transport settings may be bypassed. It always sets a `Range` header, even when not doing partial content, producing `bytes=0--1` when `count` stays `-1`. Upload helpers create unused `UseUniqueFileName` variables. Modtime precision is unsupported even though timestamps are returned as metadata.

## Test Signals
`imagekit_test.go` runs the generic rclone integration suite against `TestImageKit:` and skips fs check wrapping. There are no local unit tests for listing, URL generation, metadata mapping, or range fallback.
