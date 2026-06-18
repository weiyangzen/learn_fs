# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Open2Flags.cs

- **Purpose:** Return additional information in the response; populate the CreationTime, FileDataSize, AccessMode, ResourceType, and NMPipeStatus fields in the response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 30 lines, 794 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Open2Flags`.
- **Important APIs/types/functions:** Types: enum Open2Flags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: REQ_ATTRIB=0x0001, REQ_OPLOCK=0x0002, REQ_OPBATCH=0x0004, REQ_EASIZE=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
