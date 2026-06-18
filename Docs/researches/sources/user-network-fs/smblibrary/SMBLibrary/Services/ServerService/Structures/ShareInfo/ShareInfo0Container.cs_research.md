<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Container.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Container.cs

## Purpose
NDR container for arrays of level-0 share entries in share enumeration responses.

## APIs, Types, and Functions
Field `NDRConformantArray<ShareInfo0Entry> Entries`; methods `Read()`, `Write()`, `Add()`, `Count`, and `Level => 0`.

## Control Flow, State, and Persistence
Read consumes a count and embedded full pointer to the conformant array. Write emits current `Count` and the array pointer. `Add()` lazily creates the array. State is the in-memory entries array.

## Dependencies and Integration
Used by `ServerService.GetNetrShareEnumResponse()` for level 0.

## Risks and Test Signals
Risks include ignoring the parsed count variable and potential null pointer/count mismatch. Test empty and multi-share arrays, NDR round trips, and client enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Container.cs -->
