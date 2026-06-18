# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/PipeState.cs

- **Purpose:** If set, the named pipe is operating in message mode. If not set, the named pipe is operating in byte mode. In message mode, the system treats the bytes read or written in each I/O operation to the pipe as a message unit. The system MUST. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 25 lines, 1295 bytes. Namespace `SMBLibrary.SMB1`. Primary type `PipeState`.
- **Important APIs/types/functions:** Types: enum PipeState : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: ReadMode=0x0100, Nonblocking=0x8000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
