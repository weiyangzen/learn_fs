# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeResponse.cs

- **Purpose:** NT_TRANSACT_NOTIFY_CHANGE Response. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 53 lines, 1591 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactNotifyChangeResponse`.
- **Important APIs/types/functions:** Types: class NTTransactNotifyChangeResponse : NTTransactSubcommand. Constructors: NTTransactNotifyChangeResponse. Constants/static metadata: none. Fields/properties: FileNotifyInformationBytes. Methods/overrides: GetParameters, GetFileNotifyInformation, SetFileNotifyInformation. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_NOTIFY_CHANGE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
