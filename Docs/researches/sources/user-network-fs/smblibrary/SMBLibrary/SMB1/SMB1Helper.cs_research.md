# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Helper.cs

- **Purpose:** SMB_DATE. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 187 lines, 6222 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Helper`.
- **Important APIs/types/functions:** Types: class SMB1Helper. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: ReadNullableFileTime, ReadSMBDate, WriteSMBDate, ReadSMBTime, WriteSMBTime, ReadSMBDateTime, WriteSMBDateTime, ReadNullableSMBDateTime, ReadSMBString, WriteSMBString, ReadFixedLengthString, WriteFixedLengthString.
- **Control flow:** String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
