# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Message.cs

- **Purpose:** Each message has a single header and either a single command or multiple batched (AndX) commands. Multiple command requests or responses can be sent in a single message. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 106 lines, 3807 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Message`.
- **Important APIs/types/functions:** Types: class SMB1Message. Constructors: SMB1Message. Constants/static metadata: none. Fields/properties: Header, Commands. Methods/overrides: GetBytes, GetSMB1Message.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMBAndXCommand, SMB1Header. Wire helpers observed: ByteWriter.WriteBytes, ByteWriter.WriteByte.
- **Integration points:** Advertises its SMB command discriminator to the message layer.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, invalid setup or command values raising InvalidDataException.
- **Explicit failure paths:** ArgumentException(Invalid command sequence), InvalidDataException(Invalid SMB header signature).
