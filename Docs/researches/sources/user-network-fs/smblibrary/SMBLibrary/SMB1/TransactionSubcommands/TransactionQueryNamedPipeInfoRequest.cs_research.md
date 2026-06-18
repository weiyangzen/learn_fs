# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoRequest.cs

- **Purpose:** TRANS_QUERY_NMPIPE_INFO Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1644 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionQueryNamedPipeInfoRequest`.
- **Important APIs/types/functions:** Types: class TransactionQueryNamedPipeInfoRequest : TransactionSubcommand. Constructors: TransactionQueryNamedPipeInfoRequest. Constants/static metadata: none. Fields/properties: FID, Level. Methods/overrides: GetSetup, GetParameters. Protocol discriminator returns: TransactionSubcommandName.TRANS_QUERY_NMPIPE_INFO.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality.
