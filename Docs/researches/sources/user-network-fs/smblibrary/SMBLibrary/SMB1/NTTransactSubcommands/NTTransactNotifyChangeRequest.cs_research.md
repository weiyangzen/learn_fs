# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeRequest.cs

- **Purpose:** NT_TRANSACT_NOTIFY_CHANGE Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1830 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactNotifyChangeRequest`.
- **Important APIs/types/functions:** Types: class NTTransactNotifyChangeRequest : NTTransactSubcommand. Constructors: NTTransactNotifyChangeRequest. Constants/static metadata: SetupLength. Fields/properties: CompletionFilter, FID, WatchTree, Reserved. Methods/overrides: GetSetup. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_NOTIFY_CHANGE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** caller-level packet tests that consume this helper.
