<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/ServerServiceHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/ServerServiceHelper.cs

## Purpose
`ServerServiceHelper` queries the Windows Server Service RPC endpoint over an SMB named pipe to list shares.

## Important APIs and Types
`ListShares(INTFileStore namedPipeShare, ShareType? shareType, out NTStatus status)` calls the overload with server `*`. The overload binds to `srvsvc`, sends `NetrShareEnum` level 1, handles fragmented RPC responses, maps access-denied or unsupported results to NTSTATUS, and filters share names by optional type.

## Control Flow
After `NamedPipeHelper.BindPipe`, it builds a request PDU with little-endian RPC representation and `NetrShareEnum` opnum. It transceives the first fragment, then keeps reading from the pipe until `LastFragment` is set, concatenates response data, parses `NetrShareEnumResponse`, and extracts `ShareInfo1Entry.NetName` values.

## State, Dependencies, and Integration
The helper is stateless but opens/closes a pipe handle through the supplied file store. `SMB1Client.ListShares()` uses it after tree-connecting to `IPC$`.

## Risks and Test Signals
The pipe handle is closed only after all fragments are collected, not on early failures. Large responses depend on `maxTransmitFragmentSize`. Tests should cover share-type filtering, fragmented responses, access denied mapping, invalid PDU handling, and close-on-success behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/ServerServiceHelper.cs -->
