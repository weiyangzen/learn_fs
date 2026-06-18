<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo.cs

## Purpose
NDR union wrapper for MS-WKST workstation information levels.

## APIs, Types, and Functions
Fields are `uint Level` and `WorkstationInfoLevel Info`. Constructors support empty, level-only, concrete info, and parser forms. `Read()` handles levels 100 and 101; `Write()` validates level consistency when `Info` is non-null.

## Control Flow, State, and Persistence
Read dispatches by level to `WorkstationInfo100` or `WorkstationInfo101` and throws `NotImplementedException` otherwise. Write emits level and embedded pointer. No persistence.

## Dependencies and Integration
Used by `NetrWkstaGetInfoResponse` and `WorkstationService`.

## Risks and Test Signals
Risks include `NotImplementedException` instead of service-specific level exceptions and null-info unsupported responses. Test local and client unmarshalling for level-only error responses and level 100/101 successes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo.cs -->
