# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionPeekNamedPipeResponse.cs

- **Purpose:** TRANS_PEEK_NMPIPE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 61 lines, 2005 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionPeekNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionPeekNamedPipeResponse : TransactionSubcommand. Constructors: TransactionPeekNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: ReadDataAvailable, MessageBytesLength, NamedPipeState, ReadData. Methods/overrides: GetParameters, GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_PEEK_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
