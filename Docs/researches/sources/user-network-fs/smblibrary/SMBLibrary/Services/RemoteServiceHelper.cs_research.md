<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteServiceHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteServiceHelper.cs

## Purpose
DCE/RPC helper for bind negotiation and response PDU fragmentation around `RemoteService` implementations.

## APIs, Types, and Functions
Public members include NDR transfer syntax constants, bind-time feature constants, `GetRPCBindResponse()`, and `GetRPCResponse()`. Private `IndexOfSupportedTransferSyntax()` selects NDR v1/v2 transfer syntax.

## Control Flow, State, and Persistence
Bind responses allocate or echo association group IDs, set the secondary pipe address, swap max transmit/receive fragment sizes, and build one result per context element. Matching service interface plus supported syntax is accepted; bind-time feature syntax can receive negotiate-ack; otherwise provider rejection is returned. Request responses call the service, convert unsupported opnums into fault PDUs, and split response bytes across `ResponsePDU`s based on negotiated max fragment size. Static association group ID is process state.

## Dependencies and Integration
Used by `RPCPipeStream` for all named-pipe RPC traffic. Depends on RPC PDU, syntax, NDR, byte-reader, and fault status types.

## Risks and Test Signals
Risks include non-thread-safe static association ID increments, no guard for too-small max fragment sizes, only NDR transfer syntaxes, and unsupported-op faults only for one exception type. Test bind with accepted/rejected contexts, feature negotiation, association ID rollover, fragmented large responses, and unsupported opnum faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteServiceHelper.cs -->
