# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactCreateRequest.cs

- **Purpose:** NT_TRANSACT_CREATE Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 90 lines, 3941 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactCreateRequest`.
- **Important APIs/types/functions:** Types: class NTTransactCreateRequest : NTTransactSubcommand. Constructors: NTTransactCreateRequest. Constants/static metadata: ParametersFixedLength. Fields/properties: Flags, RootDirectoryFID, DesiredAccess, AllocationSize, ExtFileAttributes, ShareAccess, CreateDisposition, CreateOptions, ImpersonationLevel, SecurityFlags, Name, SecurityDescriptor, ExtendedAttributes. Methods/overrides: GetParameters, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_CREATE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. Some outbound methods intentionally stop with NotImplementedException, so this type currently supports inbound parsing more than full serialization.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, NTTransactSubcommand, FileFullEAInformation, SecurityDescriptor, AccessMask. Wire helpers observed: ByteReader.ReadByte, LittleEndianReader.ReadUInt32, SMB1Helper.ReadFixedLengthString.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. NotImplementedException blocks full round-trip serialization for this type. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** Unicode and OEM string alignment fixtures, tests asserting unsupported serialization paths throw NotImplementedException.
- **Explicit failure paths:** NotImplementedException.
