# sources/user-network-fs/gcsfuse/internal/gcsx/reader.go

## Scope

This file defines the shared reader contracts used by the newer gcsx read stack.

## Purpose

It provides common request/response structures and interfaces so cache readers, buffered readers, GCS readers, visual wrappers, and read managers can interoperate and fall back cleanly.

## Important APIs, Types, And Functions

- `FallbackToAnotherReader` signals that the caller should try the next reader.
- `ReadRequest` carries caller buffer, offset, optional size-check bypass, and embedded `ReadInfo`.
- `GCSReaderRequest` carries lower-level GCS buffer, offset, computed end offset, force-create-reader flag, skip-size-check flag, and read info pointer.
- `ReadResponse` carries returned data chunks, size, and optional completion callback.
- `Reader`, `ReadManager`, and `GCSReader` interfaces define the common behavior.

## Control Flow

There is no executable flow beyond interface contracts. The key protocol is that `Reader.ReadAt` either fills `ReadRequest.Buffer`, returns data slices in `ReadResponse.Data`, or returns `FallbackToAnotherReader` to allow read-manager fallback. The read manager preserves `Offset` and `Buffer` across fallback attempts.

## State And Persistence Behavior

This file has no mutable state except the package-level sentinel error. Persistence and resource ownership are delegated to concrete implementations.

## Dependencies And Integration Points

It depends on `context`, `errors`, and `gcs.MinObject`. It is consumed by read-manager, file-cache reader, shared chunk cache reader, buffered reader integration, client GCS readers, mocks, and visual wrappers.

## Risks And Maintenance Notes

The fallback sentinel is part of the cross-reader control contract; wrapping must preserve `errors.Is`. `ReadResponse.Data` plus direct buffer filling creates two data-return modes, so callers must understand both. `Callback` adds post-read lifecycle behavior that can be missed if callers only inspect size.

## Test Signals

There are no direct tests for this definitions file, but almost every read-manager and reader test exercises these contracts through successful reads, fallback errors, EOF handling, and mock expectations.
