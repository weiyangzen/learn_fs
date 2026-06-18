<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/TreeConnectHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/TreeConnectHelper.cs

## Purpose
SMB2 tree-connect and tree-disconnect handling for disk shares and `IPC$`. It resolves the requested share, checks initial access, allocates a tree ID, and returns share type, caching flags, and maximal access.

## APIs, Types, and Functions
`GetTreeConnectResponse()` and `GetTreeDisconnectResponse()` are the entry points. `GetShareCachingFlags()` maps `CachingPolicy` to SMB2 `ShareFlags`.

## Control Flow, State, and Persistence
The helper extracts the share name from the UNC path. `IPC$` maps to `NamedPipeShare` with pipe type and no caching. Disk shares are resolved from `SMBShareCollection`, cast to `FileSystemShare`, checked for read access at root, then added to the session connected-tree table. Disconnect removes the tree ID from the session. State is per-session tree mapping.

## Dependencies and Integration
Called by `SMBServer.SMB2.cs` after session setup. It integrates with share collections, named-pipe services, access events, and SMB2 response header filling in the server.

## Risks and Test Signals
Risks include broad advertised maximal access, hard `FileSystemShare` assumption for disk shares, no DFS/share capability details beyond caching, and root-only authorization. Test `IPC$`, missing shares, denied root access, all caching policies, tree ID exhaustion, disconnect, and compounded tree-connect/create behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/TreeConnectHelper.cs -->
