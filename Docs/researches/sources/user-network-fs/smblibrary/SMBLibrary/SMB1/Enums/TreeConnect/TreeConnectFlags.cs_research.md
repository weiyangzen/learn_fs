# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/TreeConnectFlags.cs

- **Purpose:** If set and SMB_Header.TID is valid, the tree connect specified by the TID in the SMB header of the request SHOULD be disconnected when the server sends the response. If this tree disconnect fails, then the error SHOULD be ignored If set. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 27 lines, 1050 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeConnectFlags`.
- **Important APIs/types/functions:** Types: enum TreeConnectFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: DisconnectTID=0x0001, ExtendedSignatures=0x0004, ExtendedResponse=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
