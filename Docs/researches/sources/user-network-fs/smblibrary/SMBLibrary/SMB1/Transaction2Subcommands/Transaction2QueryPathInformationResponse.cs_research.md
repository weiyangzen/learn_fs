# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryPathInformationResponse.cs

- **Purpose:** TRANS2_QUERY_PATH_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 78 lines, 2604 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryPathInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2QueryPathInformationResponse : Transaction2Subcommand. Constructors: Transaction2QueryPathInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: EaErrorOffset, InformationBytes. Methods/overrides: GetParameters, GetData, GetQueryInformation, SetQueryInformation, GetFileInformation, SetFileInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_PATH_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
