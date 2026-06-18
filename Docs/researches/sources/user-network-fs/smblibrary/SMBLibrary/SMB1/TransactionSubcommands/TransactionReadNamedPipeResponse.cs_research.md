# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionReadNamedPipeResponse.cs

- **Purpose:** TRANS_READ_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1190 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionReadNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionReadNamedPipeResponse : TransactionSubcommand. Constructors: TransactionReadNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: ReadData. Methods/overrides: GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_READ_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
