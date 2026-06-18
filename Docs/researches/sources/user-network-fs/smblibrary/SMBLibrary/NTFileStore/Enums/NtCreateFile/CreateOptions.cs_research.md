<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateOptions.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateOptions.cs

## Purpose
Defines the wire-level `CreateOptions` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include FILE_DIRECTORY_FILE = 0x00000001, FILE_WRITE_THROUGH = 0x00000002, FILE_SEQUENTIAL_ONLY = 0x00000004, FILE_NO_INTERMEDIATE_BUFFERING = 0x00000008, FILE_SYNCHRONOUS_IO_ALERT = 0x00000010, FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020, FILE_NON_DIRECTORY_FILE = 0x00000040, FILE_CREATE_TREE_CONNECTION = 0x00000080, FILE_COMPLETE_IF_OPLOCKED = 0x00000100, FILE_NO_EA_KNOWLEDGE = 0x00000200, FILE_OPEN_REMOTE_INSTANCE = 0x00000400, FILE_RANDOM_ACCESS = 0x00000800, FILE_DELETE_ON_CLOSE = 0x00001000, FILE_OPEN_BY_FILE_ID = 0x00002000, FILE_OPEN_FOR_BACKUP_INTENT = 0x00004000, FILE_NO_COMPRESSION = 0x00008000, FILE_OPEN_REQUIRING_OPLOCK = 0x00010000, FILE_DISALLOW_EXCLUSIVE = 0x00020000, FILE_RESERVE_OPFILTER = 0x00100000, FILE_OPEN_REPARSE_POINT = 0x00200000, FILE_OPEN_NO_RECALL = 0x00400000, FILE_OPEN_FOR_FREE_SPACE_QUERY = 0x00800000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateOptions.cs -->
