# sources/user-network-fs/rclone/backend/sia/api/types.go

## Purpose

This file defines Go structures matching the Sia daemon renter API JSON responses used by the rclone Sia backend.

## Important APIs, Types, and Functions

`DirectoriesResponse` contains directory and file slices for `/renter/dir`. `FilesResponse` and `FileResponse` wrap file metadata for list and stat endpoints. `FileInfo` mirrors Sia file fields such as access/change/create/mod times, filesize, health, redundancy, upload progress, `SiaPath`, and availability flags. `DirectoryInfo` mirrors aggregate and direct directory health, size, redundancy, file/subdirectory counts, and `SiaPath`. `Error` stores message, HTTP status text, and status code, and implements `Error()`.

## Control Flow

The backend's REST client unmarshals JSON into these types. `Error.Error` joins non-empty message and status fields, or returns a default string when both are blank.

## State and Persistence Behavior

These are transient DTOs with no persistence. Time fields are decoded into `time.Time` by Go's JSON machinery.

## Dependencies and Integration Points

The file depends only on `strings` and `time`. It is consumed by `sia.go` for listing, object metadata reads, and error handling.

## Risks and Edge Cases

The structs rely on Sia API field names staying stable. Many numeric fields are unsigned in the API but converted to signed sizes in the backend, so unexpectedly huge values could overflow when cast. `Error.Error` omits `StatusCode`, so logs may need extra wrapping for numeric diagnostics.

## Test Signals

Tests should unmarshal representative Sia daemon responses, including missing fields and error bodies, and verify `sia.go` maps file-not-found and directory-not-found messages to rclone sentinel errors.
