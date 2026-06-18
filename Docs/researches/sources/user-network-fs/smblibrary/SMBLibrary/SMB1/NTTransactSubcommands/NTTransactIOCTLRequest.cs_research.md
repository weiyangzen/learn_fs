# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLRequest.cs

- **Purpose:** NT_TRANSACT_IOCTL Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 66 lines, 1957 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactIOCTLRequest`.
- **Important APIs/types/functions:** Types: class NTTransactIOCTLRequest : NTTransactSubcommand. Constructors: NTTransactIOCTLRequest. Constants/static metadata: SetupLength. Fields/properties: FunctionCode, FID, IsFsctl, IsFlags, Data. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_IOCTL.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** caller-level packet tests that consume this helper.
