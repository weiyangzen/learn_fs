<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/INTFileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/INTFileStore.cs

## Purpose
`INTFileStore` defines SMBLibrary's server-side NT file-store contract and the notify-completion delegate used by SMB1/SMB2 server paths.

## Important APIs, Types, And Functions
The interface covers file create/close/read/write/flush/lock/unlock, directory query, file and filesystem information get/set, security descriptor get/set, notify change, cancel, and device IO control.

## Control Flow
There is no implementation control flow here. SMB server command handlers call these methods to translate protocol requests into backend storage behavior.

## State And Persistence Behavior
The interface itself has no state. Implementations decide handle identity, persistence, async notify state, and backend storage lifetime.

## Dependencies And Integration Points
Implemented by stores such as `NamedPipeStore` and local NT file stores, and consumed by SMB1/SMB2 server command processors.

## Risks
All implementations must agree on opaque handle types, error mapping, sharing semantics, security behavior, and async notify/cancel contracts or protocol handlers will misbehave.

## Test Signals
Contract tests should run the same create/read/write/query/security/ioctl scenarios against each `INTFileStore` implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/INTFileStore.cs -->
