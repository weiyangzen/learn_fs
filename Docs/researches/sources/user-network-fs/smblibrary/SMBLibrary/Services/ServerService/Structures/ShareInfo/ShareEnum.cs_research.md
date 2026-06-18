<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareEnum.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareEnum.cs

## Purpose
NDR model for `SHARE_ENUM_STRUCT` and its embedded share-enum union.

## APIs, Types, and Functions
Fields are `uint Level` and `IShareInfoContainer Info`. Constructors support empty, level-only, concrete container, and parser forms. `Read()` and `Write()` handle NDR structure/union serialization.

## Control Flow, State, and Persistence
Read parses the outer level, the duplicated union discriminant, and level 0 or 1 container pointers. Levels 2/501/502/503 throw `UnsupportedLevelException`; other levels throw `InvalidLevelException`. Write validates `Level == Info.Level` when info exists and writes the pointer. No persistence.

## Dependencies and Integration
Used by share enum requests/responses in `ServerService`.

## Risks and Test Signals
Risks include null `Info` with unsupported responses, no read support for level 2 despite service get-info support, and dependence on exact NDR union discriminant behavior. Test level 0/1 parsing and writing, unsupported level handling, invalid levels, and null-info writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareEnum.cs -->
