# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/Enums/NTTransactSubcommandName.cs

- **Purpose:** This is the Function field in SMB_COM_NT_TRANSACT request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 18 lines, 533 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactSubcommandName`.
- **Important APIs/types/functions:** Types: enum NTTransactSubcommandName : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NT_TRANSACT_CREATE=0x0001, NT_TRANSACT_IOCTL=0x0002, NT_TRANSACT_SET_SECURITY_DESC=0x0003, NT_TRANSACT_NOTIFY_CHANGE=0x0004, NT_TRANSACT_QUERY_SECURITY_DESC=0x0006, NT_TRANSACT_QUERY_QUOTA=0x0007, NT_TRANSACT_SET_QUOTA=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
