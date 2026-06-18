# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionTransactNamedPipeRequest.cs

- **Purpose:** TRANS_TRANSACT_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 55 lines, 1553 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionTransactNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionTransactNamedPipeRequest : TransactionSubcommand. Constructors: TransactionTransactNamedPipeRequest. Constants/static metadata: none. Fields/properties: FID, WriteData. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_TRANSACT_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
