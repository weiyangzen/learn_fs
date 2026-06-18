# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLResponse.cs

- **Purpose:** NT_TRANSACT_IOCTL Response. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 57 lines, 1550 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactIOCTLResponse`.
- **Important APIs/types/functions:** Types: class NTTransactIOCTLResponse : NTTransactSubcommand. Constructors: NTTransactIOCTLResponse. Constants/static metadata: ParametersLength, SetupLength. Fields/properties: TransactionDataSize, Data. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_IOCTL.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** caller-level packet tests that consume this helper.
