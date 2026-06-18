# sources/user-network-fs/rclone/backend/seafile/api/types.go

## Purpose
This file defines JSON request and response DTOs for the Seafile backend API package. It isolates Seafile's inconsistent HTTP JSON shapes behind Go structs used by the backend implementation.

## Important APIs, Types, And Functions
Authentication types include `AuthenticationRequest` and `AuthenticationResult`. Account/server/library types include `AccountInfo`, `ServerInfo`, `DefaultLibrary`, `CreateLibraryRequest`, `Library`, and `CreateLibrary`. File/directory listing types include `FileType`, `FileTypeDir`, `FileTypeFile`, `FileDetail`, `DirEntries`, `DirEntry`, and `DirectoryDetail`. Mutation types include `Operation` plus constants for copy/move/rename, `FileOperationRequest`, `FileInfo`, `CreateDirRequest`, `ShareLinkRequest`, `SharedLink`, and `BatchSourceDestRequest`.

## Control Flow
There is no executable control flow. These structs are populated by JSON marshal/unmarshal calls in other Seafile backend files. Field tags map Go names to the exact JSON keys expected or returned by Seafile endpoints.

## State And Persistence Behavior
The structs represent remote Seafile state such as libraries, files, directories, usage, auth tokens, and share links. They do not persist anything directly. The comments note duplicate shapes because different Seafile API calls return similar objects with different JSON keys or types.

## Dependencies And Integration Points
This file has no imports. It is consumed by the Seafile backend's REST API layer. The `api` package boundary keeps transport schemas separate from rclone `fs` types and backend object logic.

## Risks And Edge Cases
The main risk is schema drift or endpoint inconsistency: Seafile may return different timestamp formats (`int64` mtime vs string `last_modified`), different ID field names (`id`, `repo_id`, `obj_id`), and different object-name fields. Missing fields default to zero values, so callers must distinguish absent values from legitimate zero sizes/times where necessary. `FileType` and `Operation` are string aliases without validation.

## Test Signals
No direct tests are present in this file. Tests for Seafile API behavior would need to exercise JSON parsing and backend operations that consume these DTOs, especially mixed old/new API file detail responses and copy/move/rename responses.
