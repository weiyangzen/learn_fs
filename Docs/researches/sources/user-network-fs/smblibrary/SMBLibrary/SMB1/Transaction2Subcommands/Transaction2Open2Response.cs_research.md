# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Open2Response.cs

- **Purpose:** TRANS2_OPEN2 Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 77 lines, 3258 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2Open2Response`.
- **Important APIs/types/functions:** Types: class Transaction2Open2Response : Transaction2Subcommand. Constructors: Transaction2Open2Response. Constants/static metadata: ParametersLength. Fields/properties: FID, FileAttributes, CreationTime, FileDataSize, AccessMode, ResourceType, NMPipeStatus, ActionTaken, Reserved, ExtendedAttributeErrorOffset, ExtendedAttributeLength. Methods/overrides: GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_OPEN2.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. UTIME fields are converted between SMB seconds-since-1970 values and nullable DateTime values.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: UTimeHelper, Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, UTimeHelper.ReadNullableUTime, UTimeHelper.WriteUTime.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
