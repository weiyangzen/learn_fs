<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/Win32Error.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Enums/Win32Error.cs

## Purpose
Defines the wire-level `Win32Error` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include ERROR_SUCCESS = 0x0000, ERROR_ACCESS_DENIED = 0x0005, ERROR_SHARING_VIOLATION = 0x0020, ERROR_NOT_SUPPORTED = 0x0032, ERROR_INVALID_PARAMETER = 0x0057, ERROR_DISK_FULL = 0x0070, ERROR_INVALID_NAME = 0x007B, ERROR_INVALID_LEVEL = 0x007C, ERROR_DIR_NOT_EMPTY = 0x0091, ERROR_BAD_PATHNAME = 0x00A1, ERROR_ALREADY_EXISTS = 0x00B7, ERROR_NO_TOKEN = 0x03F0, ERROR_LOGON_FAILURE = 0x052E, ERROR_ACCOUNT_RESTRICTION = 0x052F, ERROR_INVALID_LOGON_HOURS = 0x0530, ERROR_INVALID_WORKSTATION = 0x0531, ERROR_PASSWORD_EXPIRED = 0x0532, ERROR_ACCOUNT_DISABLED = 0x0533, ERROR_LOGON_TYPE_NOT_GRANTED = 0x0569, ERROR_ACCOUNT_EXPIRED = 0x0701, ERROR_PASSWORD_MUST_CHANGE = 0x0773, ERROR_ACCOUNT_LOCKED_OUT = 0x0775, NERR_NetNameNotFound = 0x0906. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/Win32Error.cs -->
