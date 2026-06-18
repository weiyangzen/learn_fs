<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/SMBShareCollection.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/SMBShareCollection.cs

## Purpose
Typed list of `FileSystemShare` objects with case-aware lookup helpers and share-name listing.

## APIs, Types, and Functions
Extends `List<FileSystemShare>`. Methods are `Contains(string, StringComparison)`, `IndexOf(string, StringComparison)`, `ListShares()`, and `GetShareFromName()`.

## Control Flow, State, and Persistence
Lookups linearly scan the list by `FileSystemShare.Name`. `GetShareFromName()` uses ordinal-ignore-case comparison and returns null when absent. State is the inherited in-memory list.

## Dependencies and Integration
Consumed by `SMBServer`, tree-connect helpers, and `NamedPipeShare` construction.

## Risks and Test Signals
Risks include duplicate share names, mutable list operations from callers without synchronization, and linear lookup cost. Test case-insensitive lookup, duplicate behavior, empty lists, and share-list snapshots used by RPC services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/SMBShareCollection.cs -->
