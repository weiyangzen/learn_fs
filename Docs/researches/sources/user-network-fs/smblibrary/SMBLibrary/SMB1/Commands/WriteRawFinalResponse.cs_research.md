# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawFinalResponse.cs

- **Purpose:** SMB_COM_WRITE_RAW Final Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1352 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteRawFinalResponse`.
- **Important APIs/types/functions:** Types: class WriteRawFinalResponse : SMB1Command. Constructors: WriteRawFinalResponse. Constants/static metadata: ParametersLength. Fields/properties: Count. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE_COMPLETE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE_COMPLETE to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
