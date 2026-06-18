<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/NegotiateHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/NegotiateHelper.cs

## Purpose
SMB2 negotiate response construction for direct SMB2 negotiation and the SMB1-negotiation upgrade path. It selects the dialect, advertises signing and size limits, optionally enables Large MTU, grows receive buffers, and returns the initial SPNEGO token.

## APIs, Types, and Functions
Main APIs are `GetNegotiateResponse(List<string> smb2Dialects, ...)`, `GetNegotiateResponse(NegotiateRequest, ...)`, and `FindSMB2Dialects()` overloads for SMB1 negotiate messages. Constants define SMB2 dialect strings and normal/LargeMTU read/write/transact sizes.

## Control Flow, State, and Persistence
For SMB1 upgrade, `SMB 2.???` yields wildcard revision while `SMB 2.002` sets `SMBDialect.SMB202`. Direct SMB2 negotiation prefers SMB3.0 only when enabled, otherwise SMB2.1 then SMB2.0.2. Direct TCP plus non-2.0.2 enables Large MTU and may increase `state.ReceiveBuffer`. The response includes current time, server start time, server GUID, signing enabled, and security token. State change is the connection dialect and possible buffer size.

## Dependencies and Integration
Used by `SMBServer.cs` for SMB1-to-SMB2 upgrade and by `SMBServer.SMB2.cs` for initial SMB2 requests. It depends on `GSSProvider`, NetBIOS session packet sizing, and SMB dialect enums.

## Risks and Test Signals
Risks include limited SMB3 support despite selecting SMB3.0, no encryption/preauth capabilities, wildcard dialect handling that leaves `state.Dialect` unset, and receive-buffer growth tied only to LargeMTU. Test dialect preference, SMB1 upgrade, disabled SMB3, DirectTCP versus NetBIOS sizes, unsupported dialects, and returned SPNEGO tokens.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/NegotiateHelper.cs -->
