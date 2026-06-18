<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBFileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBFileStore.cs

## Purpose
`ISMBFileStore` extends `INTFileStore` with SMB tree-specific lifecycle and negotiated transfer-size properties.

## Important APIs and Types
`Disconnect()` disconnects the tree/share. `MaxReadSize` and `MaxWriteSize` expose recommended chunk sizes for read/write calls inherited from `INTFileStore`.

## Control Flow
The interface has no implementation. Consumers obtain an instance from `ISMBClient.TreeConnect()` and use inherited file APIs until disconnect.

## State, Dependencies, and Integration
`SMB1FileStore` implements this interface by delegating sizes and message send/wait behavior to its owning `SMB1Client`.

## Risks and Test Signals
`Disconnect()` is separate from closing file handles, so callers must manage handles before tree disconnect. Tests should verify max-size propagation, disconnected-tree behavior, and mapping of store operations to transport failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBFileStore.cs -->
