<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/InvalidLevelException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/InvalidLevelException.cs

## Purpose
Exception used by RPC/NDR union parsers to signal an invalid information level rather than a merely unsupported valid level.

## APIs, Types, and Functions
`InvalidLevelException : Exception` stores a private `uint m_level`, initializes it in the constructor, and exposes it via `Level`.

## Control Flow, State, and Persistence
The exception is thrown during parsing of union discriminants and caught by service handlers such as share enumeration to return `ERROR_INVALID_LEVEL`. State is only the level value.

## Dependencies and Integration
Used by server-service share/server info structures and service response construction.

## Risks and Test Signals
Risks include no message/base constructor and inconsistent namespace usage with related exceptions. Test invalid-level requests produce the intended Win32 result and preserve the requested level in the response union.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/InvalidLevelException.cs -->
