<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Container.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Container.cs

## Purpose
NDR container for arrays of level-1 share entries with name, type, and remark.

## APIs, Types, and Functions
Field `NDRConformantArray<ShareInfo1Entry> Entries`; methods `Read()`, `Write()`, `Add()`, `Count`, and `Level => 1`.

## Control Flow, State, and Persistence
Read consumes count and array pointer; write emits computed count and array pointer; add lazily allocates entries. State is in-memory only.

## Dependencies and Integration
Used by server-service level-1 share enumeration.

## Risks and Test Signals
Risks include parsed count not validated against array length and null-array serialization. Test empty and populated level-1 enumerations and client display of remarks/types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Container.cs -->
