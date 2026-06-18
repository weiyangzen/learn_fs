<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB2.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB2.cs

## Purpose
SMB2 request-chain dispatch and response-chain construction. It enforces negotiate/session/tree sequencing, supports compounded related operations with file ID propagation, routes commands to SMB2 helpers, signs responses when needed, and queues serialized SMB2 packets.

## APIs, Types, and Functions
Main methods are `ProcessSMB2RequestChain()`, two `ProcessSMB2Command()` overloads, `EnqueueResponse()`, `EnqueueResponseChain()`, `ToSMB2Dialect()`, `UpdateSMB2Header()`, and file-ID helper methods for request/response objects.

## Control Flow, State, and Persistence
Initial SMB2 requests must be negotiate; successful negotiate converts the base connection into `SMB2ConnectionState`. Later duplicate negotiate closes the socket. Session setup and echo are handled before session lookup; other commands require a valid session and, unless async cancel, a valid tree. Related compounded requests reuse generated file IDs from prior create/IOCTL responses and propagate failures. Response headers inherit message IDs, credits, session/tree IDs, and signing flags. State changes include sessions, trees, open files, async contexts, and send queue entries.

## Dependencies and Integration
Called by `SMBServer.cs` after SMB2 chain parsing. It integrates all SMB2 helper files, `ConnectionManager`, `SMB2Cryptography`, `NetBios.SessionMessagePacket`, and session signing keys.

## Risks and Test Signals
Risks include type-check dispatch maintenance, limited dialect mapping, compounding edge cases around failed or missing file IDs, signing-key selection from the first response session, and no explicit credit accounting beyond echoing request credits. Test negotiation enforcement, compounded create/read/close, unrelated compounding, async cancel, invalid tree/session, signed requests, and unsupported command errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB2.cs -->
