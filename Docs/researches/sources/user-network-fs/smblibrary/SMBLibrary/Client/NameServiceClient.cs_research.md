<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/NameServiceClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/NameServiceClient.cs

## Purpose
`NameServiceClient` performs a NetBIOS node-status query to discover a server's NetBIOS file-server name.

## Important APIs and Types
`NetBiosNameServicePort` is 137. The constructor stores the server IP address. `GetServerName()` sends a node-status request and returns the first name with `FileServerService` suffix. `SendNodeStatusRequest()` handles UDP send/receive and response parsing.

## Control Flow
The client builds a `NodeStatusRequest` for wildcard `*`, connects a UDP socket to the target endpoint, sends request bytes, blocks for a response, parses `NodeStatusResponse`, then scans returned names for the file server suffix.

## State, Dependencies, and Integration
State is the target IP address. `SMB1Client` uses this as fallback when a generic `*SMBSERVER` NetBIOS session request is rejected.

## Risks and Test Signals
There is no timeout configuration, disposal wrapper, or exception handling in this class; UDP receive can block according to socket defaults. Tests should cover response parsing with multiple names, no file-server suffix, unreachable host behavior, and integration with SMB1 NetBIOS fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/NameServiceClient.cs -->
