# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Header.cs

- **Purpose:** SMB_FLAGS2_EXTENDED_SECURITY. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 140 lines, 4672 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Header`.
- **Important APIs/types/functions:** Types: class SMB1Header. Constructors: SMB1Header. Constants/static metadata: Length, ProtocolSignature. Fields/properties: Protocol, Command, Status, Flags, Flags2, SecurityFeatures, TID, UID, MID, PID, ReplyFlag, ExtendedSecurityFlag, UnicodeFlag. Methods/overrides: WriteBytes, GetBytes, IsValidSMB1Header.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Header signing state is represented by the SecurityFeatures field but persistence is left to the surrounding SMB session. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Header, NTStatus. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianConverter.ToUInt64, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, LittleEndianWriter.WriteUInt64.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality.
