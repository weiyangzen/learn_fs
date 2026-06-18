<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteService.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteService.cs

## Purpose
Abstract base contract for RPC services exposed over SMB named pipes.

## APIs, Types, and Functions
Subclasses implement `GetResponseBytes(ushort opNum, byte[] requestBytes)`, `Guid InterfaceGuid`, and `string PipeName`.

## Control Flow, State, and Persistence
The base class has no state. Service-specific subclasses parse request bytes, dispatch opnums, and serialize response bytes.

## Dependencies and Integration
Consumed by `NamedPipeShare`, `NamedPipeStore`, `RPCPipeStream`, and `RemoteServiceHelper`.

## Risks and Test Signals
Risks include raw byte APIs that push parsing validation into each service and no explicit service version property despite constants in subclasses. Test service binding by interface GUID and request dispatch through concrete services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteService.cs -->
