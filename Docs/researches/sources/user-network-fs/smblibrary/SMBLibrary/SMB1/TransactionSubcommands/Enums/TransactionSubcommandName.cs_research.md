# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/TransactionSubcommandName.cs

- **Purpose:** The 0x0001 subcommand code is interpreted as TRANS_MAILSLOT_WRITE if the operation is being performed on a mailslot. The same code is interpreted as a TRANS_SET_NMPIPE_STATE (section 2.2.5.1) if the operation is performed on a named pipe. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 27 lines, 953 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionSubcommandName`.
- **Important APIs/types/functions:** Types: enum TransactionSubcommandName : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: TRANS_MAILSLOT_WRITE=0x0001, TRANS_SET_NMPIPE_STATE=0x0001, TRANS_RAW_READ_NMPIPE=0x0011, TRANS_QUERY_NMPIPE_STATE=0x0021, TRANS_QUERY_NMPIPE_INFO=0x0022, TRANS_PEEK_NMPIPE=0x0023, TRANS_TRANSACT_NMPIPE=0x0026, TRANS_RAW_WRITE_NMPIPE=0x0031, TRANS_READ_NMPIPE=0x0036, TRANS_WRITE_NMPIPE=0x0037, TRANS_WAIT_NMPIPE=0x0053, TRANS_CALL_NMPIPE=0x0054.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
