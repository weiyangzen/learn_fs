# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ExtendedFileAttributes.cs

- **Purpose:** SMB_EXT_FILE_ATTR. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 36 lines, 1527 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ExtendedFileAttributes`.
- **Important APIs/types/functions:** Types: enum ExtendedFileAttributes : uint. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: ReadOnly=0x00000001, Hidden=0x00000002, System=0x00000004, Directory=0x00000010, Archive=0x00000020, Normal=0x00000080, Temporary=0x00000100, Sparse=0x00000200, ReparsePoint=0x00000400, Compressed=0x00000800, Offline=0x00001000, NotIndexed=0x00002000, Encrypted=0x00004000, PosixSemantics=0x01000000, BackupSemantics=0x02000000, DeleteOnClose=0x04000000, SequentialScan=0x08000000, RandomAccess=0x10000000, NoBuffering=0x10000000, WriteThrough=0x80000000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
