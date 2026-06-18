# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWaitNamedPipeRequest.cs

- **Purpose:** TRANS_WAIT_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1349 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionWaitNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionWaitNamedPipeRequest : TransactionSubcommand. Constructors: TransactionWaitNamedPipeRequest. Constants/static metadata: none. Fields/properties: Priority. Methods/overrides: GetSetup. Protocol discriminator returns: TransactionSubcommandName.TRANS_WAIT_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
