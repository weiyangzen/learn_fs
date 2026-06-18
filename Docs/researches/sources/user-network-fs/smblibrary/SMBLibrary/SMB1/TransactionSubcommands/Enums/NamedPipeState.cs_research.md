# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/NamedPipeState.cs

- **Purpose:** Defines protocol constants for NamedPipeState. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 223 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NamedPipeState`.
- **Important APIs/types/functions:** Types: enum NamedPipeState : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: DisconnectedByServer=0x0001, Listening=0x0002, ConnectionToServerOK=0x0003, ServerEndClosed=0x0004.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
