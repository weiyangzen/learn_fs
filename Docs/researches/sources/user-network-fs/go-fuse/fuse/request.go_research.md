# `sources/user-network-fs/go-fuse/fuse/request.go`

## Purpose
Defines reusable request storage and low-level parsing/serialization helpers for raw FUSE messages.

## Important APIs, Types, And Functions
`request`, `requestAlloc`, `parseRequest`, `InputDebug`, `OutputDebug`, `setInput`, `filename`, `filenames`, `serializeHeader`, `outPayloadSize`, plus unsafe typed accessors.

## Control Flow
Reads start as byte slices, `parseRequest` chooses input/control sizes from opcode handlers and kernel settings, and output sizes are determined from handler metadata plus dynamic READ/READDIR/XATTR/IOCTL payload lengths. Serialization writes `OutHeader` with negative errno for normal replies.

## State And Persistence
`requestAlloc` carries pooled request state plus inline buffers for small input/output. `clear` resets per-request fields before reuse; read results may be direct payloads or deferred `ReadResult` objects.

## Dependencies And Integration Points
Depends on operation handler tables, protocol structs, debug printing, and unsafe layout equivalence between byte buffers and FUSE structs.

## Risks And Edge Cases
Unsafe parsing makes struct layout and short-read checks critical. INIT has version-dependent size trimming; GETXATTR/LISTXATTR switch between size query and data reply; response status sign handling must remain exact.

## Test Signals
Covered indirectly by protocol-server parsing tests, print/debug tests, and all server integration tests that exercise request lifecycles.
