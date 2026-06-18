# sources/user-network-fs/rclone/backend/storj/storj_unsupported.go

## Purpose

This build-tagged file provides an empty `storj` package on Plan 9, where the main Storj backend is not built.

## Important APIs, Types, and Functions

There are no exported APIs or functions. The file contains only `//go:build plan9` and the package declaration.

## Control Flow

On Plan 9 builds, this file satisfies package existence while excluding `fs.go`, `object.go`, and tests guarded by `!plan9`.

## State and Persistence Behavior

No state or persistence exists.

## Dependencies and Integration Points

It integrates with Go build constraints to avoid compiling unsupported Storj/uplink code on Plan 9.

## Risks and Edge Cases

The backend is unavailable on Plan 9. Any code expecting registered `storj` support on that platform will not find it.

## Test Signals

A Plan 9 package build should succeed without registering the backend. Non-Plan 9 builds should ignore this file.
