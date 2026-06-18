<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoEntry.cs

## Purpose
Interface for level-specific share information entries.

## APIs, Types, and Functions
Extends `INDRStructure` and requires `uint Level`.

## Control Flow, State, and Persistence
No implementation logic or state.

## Dependencies and Integration
Used by `ShareInfo` and concrete entries for levels 0, 1, and 2.

## Risks and Test Signals
Risk is low; callers must ensure the union level matches the concrete entry. Test concrete entry serialization through `ShareInfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoEntry.cs -->
