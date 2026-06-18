# sources/user-network-fs/rclone/backend/quatrix/api/types.go

## Purpose
Quatrix API DTOs: defines JSON payloads and helpers for Quatrix REST calls.

## Important APIs, Types, And Functions
Important surface: ProfileInfo, IDList, DeleteParams, FileInfo, File, JSONTime, upload/download/copy/move params and responses.

## Control Flow
backend serializes these for id lookup, metadata, delete, upload, finalize, copy and move; JSONTime converts fractional Unix seconds

## State And Persistence
DTOs only; represent remote file IDs, quota, timestamps, upload keys.

## Dependencies And Integration Points
strconv/time and quatrix.go REST client.

## Risks And Test Signals
Risks and useful test signals: type-code drift, float timestamp precision, project-folder semantics.
