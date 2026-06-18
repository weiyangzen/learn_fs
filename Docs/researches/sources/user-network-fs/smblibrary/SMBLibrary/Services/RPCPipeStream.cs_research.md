<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RPCPipeStream.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/RPCPipeStream.cs

## Purpose
Stream implementation for message-mode named pipes carrying DCE/RPC traffic to a single `RemoteService`. It parses incoming RPC PDUs, generates bind or request responses, and queues response messages for pipe reads.

## APIs, Types, and Functions
`RPCPipeStream : Stream` overrides `Read()`, `Write()`, `Flush()`, `Close()`, `Seek()`, `SetLength()`, and stream capability properties. `ProcessRPCRequest()` handles bind, request, and protocol-error cases. `MessageLength` exposes the first queued message length.

## Control Flow, State, and Persistence
`Write()` treats each write as one pipe message and parses one `RPCPDU`. Bind requests produce a `BindAckPDU` and set `m_maxTransmitFragmentSize`. Later request PDUs are dispatched through `RemoteServiceHelper.GetRPCResponse()` and may append multiple fragmented responses. Reads drain the first queued `MemoryStream` and remove it at EOF. State is per-stream service reference, output queue, and negotiated transmit fragment size.

## Dependencies and Integration
Used by named-pipe file-store plumbing for services such as `srvsvc` and `wkssvc`. Depends on RPC PDU classes and `RemoteServiceHelper`.

## Risks and Test Signals
Risks include no handling for fragmented incoming request PDUs, no synchronization on the output queue, empty `Close()`, and protocol-error behavior when a request arrives before bind. Test bind negotiation, request after bind, unsupported op fault, fragmented response reads, read-empty returning 0, and invalid PDU ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RPCPipeStream.cs -->
