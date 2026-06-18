# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoResponse.cs

- **Purpose:** TRANS_QUERY_NMPIPE_INFO Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 71 lines, 2611 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionQueryNamedPipeInfoResponse`.
- **Important APIs/types/functions:** Types: class TransactionQueryNamedPipeInfoResponse : TransactionSubcommand. Constructors: TransactionQueryNamedPipeInfoResponse. Constants/static metadata: ParametersLength. Fields/properties: OutputBufferSize, InputBufferSize, MaximumInstances, CurrentInstances, PipeNameLength, PipeName. Methods/overrides: GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_QUERY_NMPIPE_INFO.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, TransactionSubcommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
