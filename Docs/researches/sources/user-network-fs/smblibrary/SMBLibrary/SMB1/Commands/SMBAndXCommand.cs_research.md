# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMBAndXCommand.cs

- **Purpose:** Defines SMBAndXCommand for the SMB1 command packet layer. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1650 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMBAndXCommand`.
- **Important APIs/types/functions:** Types: class SMBAndXCommand : SMB1Command. Constructors: SMBAndXCommand. Constants/static metadata: none. Fields/properties: AndXCommand, AndXReserved, AndXOffset. Methods/overrides: GetBytes, WriteAndXOffset.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMBAndXCommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
