# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/OptionalSupportFlags.cs

- **Purpose:** The server supports the use of SMB_FILE_ATTRIBUTES exclusive search attributes in client requests. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 22 lines, 694 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OptionalSupportFlags`.
- **Important APIs/types/functions:** Types: enum OptionalSupportFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_SUPPORT_SEARCH_BITS=0x0001, SMB_SHARE_IS_IN_DFS=0x0002, SMB_CSC_CACHE_MANUAL_REINT=0x0000, SMB_CSC_CACHE_AUTO_REINT=0x0004, SMB_CSC_CACHE_VDO=0x0008, SMB_CSC_NO_CACHING=0x000C, SMB_UNIQUE_FILE_NAME=0x0010, SMB_EXTENDED_SIGNATURES=0x0020.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
