<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Exceptions/UnsupportedInformationLevelException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Exceptions/UnsupportedInformationLevelException.cs

## Purpose
`UnsupportedInformationLevelException` is a focused exception for unsupported SMB/NT information class requests.

## Important APIs, Types, And Functions
It exposes the default `Exception` constructor and a message constructor.

## Control Flow
There is no custom control flow beyond base exception construction.

## State And Persistence Behavior
No mutable state beyond standard exception fields.

## Dependencies And Integration Points
Thrown by file-information and filesystem-information factories when a requested class has no implementation.

## Risks
Risk is inconsistent mapping from this exception to SMB status codes by callers.

## Test Signals
Test unsupported information-class requests through factories and server/client query paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Exceptions/UnsupportedInformationLevelException.cs -->
