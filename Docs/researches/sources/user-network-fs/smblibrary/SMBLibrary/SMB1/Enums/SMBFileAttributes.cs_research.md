# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/SMBFileAttributes.cs

- **Purpose:** SMB_FILE_ATTRIBUTES. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 24 lines, 889 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMBFileAttributes`.
- **Important APIs/types/functions:** Types: enum SMBFileAttributes : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: Normal=0x0000, ReadOnly=0x0001, Hidden=0x0002, System=0x0004, Volume=0x0008, Directory=0x0010, Archive=0x0020, SearchReadOnly=0x0100, SearchHidden=0x0200, SearchSystem=0x0400, SearchDirectory=0x1000, SearchArchive=0x2000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
