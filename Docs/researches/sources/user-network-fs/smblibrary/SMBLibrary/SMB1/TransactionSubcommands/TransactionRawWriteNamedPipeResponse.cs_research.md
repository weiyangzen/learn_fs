# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawWriteNamedPipeResponse.cs

- **Purpose:** TRANS_RAW_WRITE_NMPIPE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1302 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionRawWriteNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionRawWriteNamedPipeResponse : TransactionSubcommand. Constructors: TransactionRawWriteNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: BytesWritten. Methods/overrides: GetParameters. Protocol discriminator returns: TransactionSubcommandName.TRANS_RAW_WRITE_NMPIPE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality.
