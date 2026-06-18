# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeStateRequest.cs

- **Purpose:** TRANS_QUERY_NMPIPE_STATE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 44 lines, 1247 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionQueryNamedPipeStateRequest`.
- **Important APIs/types/functions:** Types: class TransactionQueryNamedPipeStateRequest : TransactionSubcommand. Constructors: TransactionQueryNamedPipeStateRequest. Constants/static metadata: none. Fields/properties: FID. Methods/overrides: GetSetup. Protocol discriminator returns: TransactionSubcommandName.TRANS_QUERY_NMPIPE_STATE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality.
