<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedLevelException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedLevelException.cs

## Purpose
Exception used when an RPC information level is recognized by the protocol but not implemented by this server.

## APIs, Types, and Functions
`UnsupportedLevelException : Exception` stores and exposes a `uint Level` through a constructor and read-only property.

## Control Flow, State, and Persistence
Thrown by NDR structures such as `ShareEnum` for known-but-unsupported levels and caught by `ServerService` to produce `ERROR_NOT_SUPPORTED`. No persistence.

## Dependencies and Integration
Integrated with server-service request parsing and response union construction.

## Risks and Test Signals
Risks mirror invalid-level handling: no message, limited stack context, and callers must catch it distinctly. Test levels 2/501/502/503 in share enumeration and confirm `ERROR_NOT_SUPPORTED` rather than invalid-level.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedLevelException.cs -->
