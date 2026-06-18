# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2CreateDirectoryRequest.cs

- **Purpose:** TRANS2_CREATE_DIRECTORY Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 63 lines, 2110 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2CreateDirectoryRequest`.
- **Important APIs/types/functions:** Types: class Transaction2CreateDirectoryRequest : Transaction2Subcommand. Constructors: Transaction2CreateDirectoryRequest. Constants/static metadata: none. Fields/properties: Reserved, DirectoryName, ExtendedAttributeList. Methods/overrides: GetSetup, GetParameters, GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_CREATE_DIRECTORY.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, Transaction2Subcommand, FullExtendedAttributeList. Wire helpers observed: LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
