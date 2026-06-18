# `sources/user-network-fs/go-fuse/fuse/protocol-server.go`

## Purpose
Provides an in-process protocol dispatcher from raw FUSE request buffers to a `RawFileSystem`, plus an experimental `ProtocolServer` for virtiofs-style IOV request handling without a mounted `/dev/fuse` fd.

## Important APIs, Types, And Functions
Defines `protocolServer`, `ProtocolServer`, `NewProtocolServer`, `HandleRequest`, interrupt tracking methods, `iovLen`, and `iovLens`.

## Control Flow
`handleRequest` marks requests inflight, logs input, handles the poll hack, rejects missing handlers, runs the opcode handler under panic recovery, suppresses eligible replies, and serializes output. `HandleRequest` flattens header/control IOVs, validates output IOV shape, dispatches, and returns the exact written descriptor length.

## State And Persistence
Tracks inflight requests under `interruptMu`, a connection-dead flag for cancellation, latency recorder, kernel settings, mount options, and notify-retrieve wait table.

## Dependencies And Integration Points
Uses operation handlers from the raw protocol layer, `request` parsing/serialization, and `MountOptions` panic/debug behavior. The public wrapper forces `DisableSplice` because in-process dispatch cannot splice to a kernel fd.

## Risks And Edge Cases
IOV shape validation must be strict to avoid corrupting guest/device buffers. Interrupt cancellation is linear over inflight requests and rare by design. Panic handling relies on user-supplied handler returning a nonzero status.

## Test Signals
`protocol-server_test.go` feeds a GETXATTR-like IOV request and verifies header length/status serialization against the default raw filesystem.
