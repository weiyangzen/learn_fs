<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/ISMBShare.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/ISMBShare.cs

## Purpose
Minimal common interface for SMB shares, allowing disk shares and named-pipe shares to be used by protocol handlers through a shared name and file-store contract.

## APIs, Types, and Functions
`ISMBShare` declares read-only `Name` and `INTFileStore FileStore` properties.

## Control Flow, State, and Persistence
The interface has no implementation state. Implementations decide whether the file store maps to a file system or named-pipe service store.

## Dependencies and Integration
Implemented by `FileSystemShare` and `NamedPipeShare`; consumed throughout SMB1/SMB2 helpers after tree lookup.

## Risks and Test Signals
Risks are mainly type narrowing: many helpers cast to `FileSystemShare`, so the abstraction is only partial. Test custom share implementations against helpers that do and do not require disk-specific access behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/ISMBShare.cs -->
