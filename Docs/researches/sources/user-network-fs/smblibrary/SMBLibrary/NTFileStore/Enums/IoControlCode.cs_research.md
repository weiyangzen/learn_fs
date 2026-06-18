<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/IoControlCode.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/IoControlCode.cs

## Purpose
Defines the wire-level `IoControlCode` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FSCTL_DFS_GET_REFERRALS = 0x00060194, FSCTL_DFS_GET_REFERRALS_EX = 0x000601B0, FSCTL_IS_PATHNAME_VALID = 0x0009002C, FSCTL_GET_COMPRESSION = 0x0009003C, FSCTL_FILESYSTEM_GET_STATISTICS = 0x00090060, FSCTL_QUERY_FAT_BPB = 0x00090058, FSCTL_GET_NTFS_VOLUME_DATA = 0x00090064, FSCTL_GET_RETRIEVAL_POINTERS = 0x00090073, FSCTL_FIND_FILES_BY_SID = 0x0009008F, FSCTL_SET_OBJECT_ID = 0x00090098, FSCTL_GET_OBJECT_ID = 0x0009009C, FSCTL_DELETE_OBJECT_ID = 0x000900A0, FSCTL_SET_REPARSE_POINT = 0x000900A4, FSCTL_GET_REPARSE_POINT = 0x000900A8, FSCTL_DELETE_REPARSE_POINT = 0x000900AC, FSCTL_SET_OBJECT_ID_EXTENDED = 0x000900BC, FSCTL_CREATE_OR_GET_OBJECT_ID = 0x000900C0, FSCTL_SET_SPARSE = 0x000900C4, FSCTL_READ_FILE_USN_DATA = 0x000900EB, FSCTL_WRITE_USN_CLOSE_RECORD = 0x000900EF, FSCTL_QUERY_SPARING_INFO = 0x00090138, FSCTL_QUERY_ON_DISK_VOLUME_INFO = 0x0009013C, FSCTL_SET_ZERO_ON_DEALLOCATION = 0x00090194, FSCTL_QUERY_FILE_REGIONS = 0x00090284, FSCTL_QUERY_SHARED_VIRTUAL_DISK_SUPPORT = 0x00090300, FSCTL_SVHDX_SYNC_TUNNEL_REQUEST = 0x00090304, FSCTL_STORAGE_QOS_CONTROL = 0x00090350, FSCTL_SVHDX_ASYNC_TUNNEL_REQUEST = 0x00090364, FSCTL_QUERY_ALLOCATED_RANGES = 0x000940CF, FSCTL_OFFLOAD_READ = 0x00094264, FSCTL_SET_ZERO_DATA = 0x000980C8, FSCTL_SET_DEFECT_MANAGEMENT = 0x00098134, FSCTL_FILE_LEVEL_TRIM = 0x00098208, FSCTL_OFFLOAD_WRITE = 0x00098268, FSCTL_DUPLICATE_EXTENTS_TO_FILE = 0x00098344, FSCTL_SET_COMPRESSION = 0x0009C040, FSCTL_PIPE_WAIT = 0x00110018, FSCTL_PIPE_PEEK = 0x0011400C, FSCTL_PIPE_TRANSCEIVE = 0x0011C017, FSCTL_SRV_REQUEST_RESUME_KEY = 0x00140078. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/IoControlCode.cs -->
