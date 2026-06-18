<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfoLevel.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfoLevel.cs

## Purpose
Abstract base for concrete workstation-info NDR structures.

## APIs, Types, and Functions
Declares abstract `Read(NDRParser)`, `Write(NDRWriter)`, and `uint Level`.

## Control Flow, State, and Persistence
No implementation state. Concrete subclasses own their fields and serialization.

## Dependencies and Integration
Used by `WorkstationInfo`, `WorkstationInfo100`, and `WorkstationInfo101`.

## Risks and Test Signals
Risk is low; caller code must maintain level consistency. Test concrete classes through the union wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfoLevel.cs -->
