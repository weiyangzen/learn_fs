# `sources/user-network-fs/go-fuse/fuse/splice_linux.go`

## Purpose
Linux zero-copy read path using pipe splice pairs.

## Important APIs, Types, And Functions
Defines `setSplice`, `trySplice`, `pipeReadResult`, and `ReadResultPipe`.

## Control Flow
Defines `setSplice`, `trySplice`, `pipeReadResult`, and `ReadResultPipe`.

## State And Persistence
Uses splice pipe pairs as transient state; short fd reads drain/rewrite headers and recurse through a pipe-backed result. Integrated by `server_linux.go`. Risks include pipe growth, fd lifetime, EOF short read length correction, and cleanup via `Done`.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Uses splice pipe pairs as transient state; short fd reads drain/rewrite headers and recurse through a pipe-backed result. Integrated by `server_linux.go`. Risks include pipe growth, fd lifetime, EOF short read length correction, and cleanup via `Done`.

## Test Signals
Uses splice pipe pairs as transient state; short fd reads drain/rewrite headers and recurse through a pipe-backed result. Integrated by `server_linux.go`. Risks include pipe growth, fd lifetime, EOF short read length correction, and cleanup via `Done`.
