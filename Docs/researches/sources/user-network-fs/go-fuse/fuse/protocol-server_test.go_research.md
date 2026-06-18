# `sources/user-network-fs/go-fuse/fuse/protocol-server_test.go`

## Purpose
Tests the experimental `ProtocolServer.HandleRequest` IOV path.

## Important APIs, Types, And Functions
`TestProtocolServerParse` sends a split GETXATTR request, captures debug logs, and checks output header length and ENOSYS status.

## Control Flow
`TestProtocolServerParse` sends a split GETXATTR request, captures debug logs, and checks output header length and ENOSYS status.

## State And Persistence
State is local byte buffers. The signal protects IOV flattening, output descriptor length calculation, and negative status encoding.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is local byte buffers. The signal protects IOV flattening, output descriptor length calculation, and negative status encoding.

## Test Signals
State is local byte buffers. The signal protects IOV flattening, output descriptor length calculation, and negative status encoding.
