<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/FileAccessMask.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/FileAccessMask.cs

## Purpose
Defines the wire-level `FileAccessMask` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include FILE_READ_DATA = 0x00000001, FILE_WRITE_DATA = 0x00000002, FILE_APPEND_DATA = 0x00000004, FILE_READ_EA = 0x00000008, FILE_WRITE_EA = 0x00000010, FILE_EXECUTE = 0x00000020, FILE_DELETE_CHILD = 0x00000040, FILE_READ_ATTRIBUTES = 0x00000080, FILE_WRITE_ATTRIBUTES = 0x00000100, DELETE = 0x00010000, READ_CONTROL = 0x00020000, WRITE_DAC = 0x00040000, WRITE_OWNER = 0x00080000, SYNCHRONIZE = 0x00100000, ACCESS_SYSTEM_SECURITY = 0x01000000, MAXIMUM_ALLOWED = 0x02000000, GENERIC_ALL = 0x10000000, GENERIC_EXECUTE = 0x20000000, GENERIC_WRITE = 0x40000000, GENERIC_READ = 0x80000000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/FileAccessMask.cs -->
