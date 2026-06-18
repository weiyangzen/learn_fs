<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/NTStatus.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Enums/NTStatus.cs

## Purpose
Defines the wire-level `NTStatus` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include STATUS_SUCCESS = 0x00000000, STATUS_PENDING = 0x00000103, STATUS_NOTIFY_CLEANUP = 0x0000010B, STATUS_NOTIFY_ENUM_DIR = 0x0000010C, SEC_I_CONTINUE_NEEDED = 0x00090312, STATUS_OBJECT_NAME_EXISTS = 0x40000000, STATUS_BUFFER_OVERFLOW = 0x80000005, STATUS_NO_MORE_FILES = 0x80000006, SEC_E_SECPKG_NOT_FOUND = 0x80090305, SEC_E_INVALID_TOKEN = 0x80090308, STATUS_NOT_IMPLEMENTED = 0xC0000002, STATUS_INVALID_INFO_CLASS = 0xC0000003, STATUS_INFO_LENGTH_MISMATCH = 0xC0000004, STATUS_INVALID_HANDLE = 0xC0000008, STATUS_INVALID_PARAMETER = 0xC000000D, STATUS_NO_SUCH_DEVICE = 0xC000000E, STATUS_NO_SUCH_FILE = 0xC000000F, STATUS_INVALID_DEVICE_REQUEST = 0xC0000010, STATUS_END_OF_FILE = 0xC0000011, STATUS_MORE_PROCESSING_REQUIRED = 0xC0000016, STATUS_ACCESS_DENIED = 0xC0000022, STATUS_BUFFER_TOO_SMALL = 0xC0000023, STATUS_OBJECT_NAME_INVALID = 0xC0000033, STATUS_OBJECT_NAME_NOT_FOUND = 0xC0000034, STATUS_OBJECT_NAME_COLLISION = 0xC0000035, STATUS_OBJECT_PATH_INVALID = 0xC0000039, STATUS_OBJECT_PATH_NOT_FOUND = 0xC000003A, STATUS_OBJECT_PATH_SYNTAX_BAD = 0xC000003B, STATUS_DATA_ERROR = 0xC000003E, STATUS_SHARING_VIOLATION = 0xC0000043, STATUS_FILE_LOCK_CONFLICT = 0xC0000054, STATUS_LOCK_NOT_GRANTED = 0xC0000055, STATUS_DELETE_PENDING = 0xC0000056, STATUS_IO_TIMEOUT = 0xC00000B5, STATUS_PRIVILEGE_NOT_HELD = 0xC0000061, STATUS_WRONG_PASSWORD = 0xC000006A, STATUS_LOGON_FAILURE = 0xC000006D, STATUS_ACCOUNT_RESTRICTION = 0xC000006E, STATUS_INVALID_LOGON_HOURS = 0xC000006F, STATUS_INVALID_WORKSTATION = 0xC0000070. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/NTStatus.cs -->
