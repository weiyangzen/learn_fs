# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactQuerySecurityDescriptorRequest.cs

- **Purpose:** NT_TRANSACT_QUERY_SECURITY_DESC Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 53 lines, 1803 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactQuerySecurityDescriptorRequest`.
- **Important APIs/types/functions:** Types: class NTTransactQuerySecurityDescriptorRequest : NTTransactSubcommand. Constructors: NTTransactQuerySecurityDescriptorRequest. Constants/static metadata: ParametersLength. Fields/properties: FID, Reserved, SecurityInfoFields. Methods/overrides: GetParameters. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_QUERY_SECURITY_DESC.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
