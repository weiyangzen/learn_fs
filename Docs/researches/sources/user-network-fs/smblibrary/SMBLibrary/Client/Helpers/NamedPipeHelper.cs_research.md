<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NamedPipeHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NamedPipeHelper.cs

## Purpose
`NamedPipeHelper` opens an SMB named pipe and performs the initial DCERPC bind.

## Important APIs and Types
`BindPipe(INTFileStore namedPipeShare, string pipeName, Guid interfaceGuid, uint interfaceVersion, out object pipeHandle, out int maxTransmitFragmentSize)` opens the pipe, constructs a `BindPDU`, sends it via `FSCTL_PIPE_TRANSCEIVE`, parses a `BindAckPDU`, and returns the negotiated transmit fragment size.

## Control Flow
It creates the pipe with read/write data access and share read/write. It sets RPC data representation to ASCII, little-endian, IEEE floating point, configures 5680 byte fragment sizes, adds one presentation context with the target interface and NDR transfer syntax, transceives the bind PDU, and validates the bind ACK.

## State, Dependencies, and Integration
The caller owns the returned pipe handle and must close it. `ServerServiceHelper` uses this helper before issuing `NetrShareEnum`.

## Risks and Test Signals
Failures after `CreateFile` do not close the pipe handle. Only one transfer syntax/context is attempted. Tests should cover create failure, non-ACK response, max-fragment propagation, handle cleanup expectations, and interoperability with srvsvc named pipe.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NamedPipeHelper.cs -->
