# sources/user-network-fs/rclone/backend/gofile/api/types.go

## Purpose
This file defines JSON DTOs and small helpers for the Gofile API used by the backend.

## Important APIs, Types, And Control Flow
`Time` marshals and unmarshals RFC3339 timestamps. `Error` wraps Gofile's string status, implements `error`, and provides `IsError` and `Err` helpers used after REST calls. Core resource models are `Item`, `DirectLink`, `Contents`, `Metadata`, account response types, create/delete/upload/direct-link/update/move/copy request and response types, and `UploadServerStatus`. `ToNativeTime` and `FromNativeTime` convert between Go `time.Time` and Gofile's Unix timestamp values. `DirectUploadURL` returns the upload endpoint.

## State And Persistence
The file has no runtime state. It models API payloads that describe persistent Gofile server state such as folders, files, direct links, account stats, md5 checksums, and item modtimes.

## Dependencies And Integration Points
It depends only on `fmt` and `time`. The backend consumes these types through rclone's `rest.Client` JSON calls and maps `Item` fields into rclone objects/directories.

## Risks And Test Signals
Risks are API schema drift, especially status strings, child pagination metadata, direct-link payload shape, and timestamp format. Tests should decode representative success and error bodies, paged content responses, delete result maps, and upload/direct-link responses.
