<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedOpNumException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedOpNumException.cs

## Purpose
Exception used by RPC service implementations to indicate an unsupported operation number.

## APIs, Types, and Functions
`UnsupportedOpNumException : Exception` has a default constructor and no additional fields.

## Control Flow, State, and Persistence
Thrown by `RemoteService.GetResponseBytes()` implementations for unknown opnums and caught by `RemoteServiceHelper.GetRPCResponse()` to emit an RPC fault with `OpRangeError`.

## Dependencies and Integration
Used by `ServerService`, `WorkstationService`, and RPC response framing. It is declared in namespace `SMBLibrary`, which is imported by services.

## Risks and Test Signals
Risks include lack of opnum detail and namespace inconsistency with other service exceptions. Test unsupported srvsvc/wkssvc opnums produce fault PDUs with `DidNotExecute` and op-range status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedOpNumException.cs -->
