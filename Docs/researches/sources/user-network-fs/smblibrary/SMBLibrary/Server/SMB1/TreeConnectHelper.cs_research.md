<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TreeConnectHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TreeConnectHelper.cs

## Purpose
SMB1 tree-connect command handling for disk shares and the special `IPC$` named-pipe share. It validates the requested service type, resolves the UNC share name, checks share-level access for disk roots, allocates a SMB1 tree ID, and builds normal or extended `TreeConnectAndX` responses.

## APIs, Types, and Functions
The main entry points are `TreeConnectHelper.GetTreeConnectResponse()` and `GetTreeDisconnectResponse()`. Private helpers map `CachingPolicy` to SMB1 `OptionalSupportFlags` and build `TreeConnectAndXResponse` or `TreeConnectAndXResponseExtended` with maximal access masks.

## Control Flow, State, and Persistence
The helper reads the active `SMB1Session` from `SMB1ConnectionState`, parses `request.Path` with `ServerPathUtils.GetShareName()`, chooses either `NamedPipeShare` or `SMBShareCollection.GetShareFromName()`, and stores successful connections in the session with `AddConnectedTree()`. Disconnect removes the tree from the session. No durable persistence is used; state is per connection/session.

## Dependencies and Integration
Integrated from `SMBServer.SMB1.cs` after UID validation. It depends on SMB1 command models, `NamedPipeShare`, `FileSystemShare`, `SMBShareCollection`, access checks driven by `AccessRequested`, and server logging.

## Risks and Test Signals
Risks include casts to `FileSystemShare` for non-IPC shares, share-root access checks that may not reflect path-specific policy, and extended response access masks that advertise broad rights independent of the backing store. Test SMB1 tree connect to missing shares, wrong service type, denied root access, `IPC$`, caching-policy variants, tree ID exhaustion, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TreeConnectHelper.cs -->
