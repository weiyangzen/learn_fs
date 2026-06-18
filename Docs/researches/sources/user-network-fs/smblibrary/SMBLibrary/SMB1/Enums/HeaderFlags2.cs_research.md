# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/HeaderFlags2.cs

- **Purpose:** Indicates that the client or server supports extended security. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 25 lines, 944 bytes. Namespace `SMBLibrary.SMB1`. Primary type `HeaderFlags2`.
- **Important APIs/types/functions:** Types: enum HeaderFlags2 : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: LongNamesAllowed=0x0001, ExtendedAttributes=0x0002, SecuritySignature=0x0004, CompressedData=0x0008, SecuritySignatureRequired=0x0010, LongNameUsed=0x0040, ReparsePath=0x400, ExtendedSecurity=0x0800, DFS=0x1000, ReadIfExecute=0x2000, NTStatusCode=0x4000, Unicode=0x8000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
