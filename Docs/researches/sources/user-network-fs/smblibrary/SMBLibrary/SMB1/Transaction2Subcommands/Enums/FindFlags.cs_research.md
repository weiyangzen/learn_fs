# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/FindFlags.cs

- **Purpose:** Defines protocol constants for FindFlags. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 14 lines, 329 bytes. Namespace `SMBLibrary.SMB1`. Primary type `FindFlags`.
- **Important APIs/types/functions:** Types: enum FindFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_FIND_CLOSE_AFTER_REQUEST=0x0001, SMB_FIND_CLOSE_AT_EOS=0x0002, SMB_FIND_RETURN_RESUME_KEYS=0x0004, SMB_FIND_CONTINUE_FROM_LAST=0x0008, SMB_FIND_WITH_BACKUP_INTENT=0x0010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
