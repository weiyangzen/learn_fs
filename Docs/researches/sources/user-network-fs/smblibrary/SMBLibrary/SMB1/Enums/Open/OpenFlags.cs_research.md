# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenFlags.cs

- **Purpose:** If this bit is set, the client requests that the file attribute data in the response be populated. All fields after the FID in the response are also populated. If this bit is not set, all fields after the FID in the response are zero. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 31 lines, 925 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpenFlags`.
- **Important APIs/types/functions:** Types: enum OpenFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: REQ_ATTRIB=0x0001, REQ_OPLOCK=0x0002, REQ_OPLOCK_BATCH=0x0004, SMB_OPEN_EXTENDED_RESPONSE=0x0010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
