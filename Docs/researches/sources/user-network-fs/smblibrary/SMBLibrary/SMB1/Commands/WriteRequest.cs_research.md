# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRequest.cs

- **Purpose:** SMB_COM_WRITE Request. This command is obsolete. Windows NT4 SP6 will send this command with empty data for some reason. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 83 lines, 3156 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteRequest`.
- **Important APIs/types/functions:** Types: class WriteRequest : SMB1Command. Constructors: WriteRequest. Constants/static metadata: ParametersLength, SupportedBufferFormat. Fields/properties: FID, CountOfBytesToWrite, WriteOffsetInBytes, EstimateOfRemainingBytesToBeWritten, BufferFormat, Data. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: SMB1Command. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, invalid setup or command values raising InvalidDataException, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** InvalidDataException(Unsupported Buffer Format), ArgumentException(Invalid Data length).
