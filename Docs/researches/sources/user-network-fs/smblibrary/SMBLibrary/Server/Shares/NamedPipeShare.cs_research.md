<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/NamedPipeShare.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/NamedPipeShare.cs

## Purpose
Represents the SMB `IPC$` share and exposes named-pipe-backed RPC services through an `INTFileStore`.

## APIs, Types, and Functions
`NamedPipeShare.NamedPipeShareName` is `IPC$`. The constructor builds a `NamedPipeStore` from `ServerService` and `WorkstationService`. Properties expose `Name` and `FileStore`.

## Control Flow, State, and Persistence
Construction snapshots the supplied share-name list for `ServerService` enumeration and uses machine name for server/workstation service identity. Runtime file operations are delegated to `NamedPipeStore`; there is no durable persistence.

## Dependencies and Integration
Used automatically by `SMBServer` constructor and tree-connect helpers when clients connect to `IPC$`. It integrates with RPC service classes and named-pipe file-store support.

## Risks and Test Signals
Risks include share list staleness after server construction, limited service coverage, and machine-name based identity that may not match configured NetBIOS names. Test `IPC$` tree connect, opening `srvsvc` and `wkssvc`, share enumeration matching configured shares, and unsupported pipe/service behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/NamedPipeShare.cs -->
