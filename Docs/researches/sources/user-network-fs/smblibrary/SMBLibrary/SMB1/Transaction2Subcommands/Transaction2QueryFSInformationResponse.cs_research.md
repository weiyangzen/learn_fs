# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFSInformationResponse.cs

- **Purpose:** TRANS2_QUERY_FS_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 70 lines, 2330 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryFSInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2QueryFSInformationResponse : Transaction2Subcommand. Constructors: Transaction2QueryFSInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: InformationBytes. Methods/overrides: GetData, GetQueryFSInformation, SetQueryFSInformation, GetFileSystemInformation, SetFileSystemInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_FS_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
