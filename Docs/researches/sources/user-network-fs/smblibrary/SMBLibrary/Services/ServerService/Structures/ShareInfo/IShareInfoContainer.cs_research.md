<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoContainer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoContainer.cs

## Purpose
Interface for NDR share enumeration containers.

## APIs, Types, and Functions
Extends `INDRStructure` and requires a `uint Level` property.

## Control Flow, State, and Persistence
No logic or state. Implemented by level-specific container classes.

## Dependencies and Integration
Used by `ShareEnum` to store level-specific arrays.

## Risks and Test Signals
Risk is low; level mismatch validation occurs in `ShareEnum.Write()`. Test containers through share enum responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoContainer.cs -->
