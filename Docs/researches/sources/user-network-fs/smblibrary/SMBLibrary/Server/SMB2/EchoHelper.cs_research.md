<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/EchoHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/EchoHelper.cs

## Purpose
Provides an unsolicited SMB2 echo response used by the server keepalive path. It sets the special all-ones message ID so clients do not match the packet to an outstanding request.

## APIs, Types, and Functions
`EchoHelper.GetUnsolicitedEchoResponse()` returns an `EchoResponse` with `Header.MessageID = 0xFFFFFFFFFFFFFFFF`.

## Control Flow, State, and Persistence
There is no mutable state. The helper only constructs a response object; queuing and transport are handled by the connection manager/server.

## Dependencies and Integration
Used by inactivity keepalive logic in the server/connection layer rather than normal request dispatch, where regular echo handling directly returns `new EchoResponse()`.

## Risks and Test Signals
Risks are limited to client compatibility: the SMB2 comment notes clients discard non-oplock-break unsolicited packets by spec, so this is a connection liveness nudge rather than a semantic echo. Test that keepalive packets serialize with the special message ID and do not disrupt outstanding SMB2 request tracking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/EchoHelper.cs -->
