# sources/user-network-fs/rclone/backend/sugarsync/api/types.go

## Purpose

This file defines XML request and response structures for the SugarSync REST API used by the rclone backend.

## Important APIs, Types, and Functions

Authentication types include `AppAuthorization`, `TokenAuthRequest`, and `Authorization`. Storage resource types include `File`, `Collection`, `CollectionContents`, and `User`. Mutation payloads include `CreateFolder`, `MoveFolder`, `CreateSyncFolder`, `CreateFile`, `MoveFile`, `CopyFile`, `PublicLink`, `SetPublicLink`, and `SetLastModified`.

## Control Flow

The backend marshals these structs to XML for auth, folder/file creation, moves, copies, public-link toggles, and metadata updates. It unmarshals API XML into file, collection, collection-contents, user, and auth response structs.

## State and Persistence Behavior

The types are transient DTOs. Fields such as refs, parent links, file data URLs, public links, quota, and deleted-folder links represent remote SugarSync state but are not persisted locally by this file.

## Dependencies and Integration Points

It depends on `encoding/xml` and `time`. `sugarsync.go` uses the types for all SugarSync XML calls through rclone's `rest.Client`.

## Risks and Edge Cases

The structs rely on SugarSync XML names and nested shapes staying stable. Some fields are URLs or resource refs rather than simple IDs, so callers must pass them back exactly. `Collection.Type` is an attribute and root sync folders require API-version quirks handled in `sugarsync.go`.

## Test Signals

Useful tests marshal/unmarshal representative XML from SugarSync, including public-link and quota responses, and verify backend methods build expected XML for create, move, copy, and authorization requests.
