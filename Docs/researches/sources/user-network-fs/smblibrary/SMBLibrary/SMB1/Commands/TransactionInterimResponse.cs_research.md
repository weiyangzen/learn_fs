# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionInterimResponse.cs

- **Purpose:** SMB_COM_TRANSACTION Interim Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 41 lines, 1094 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionInterimResponse`.
- **Important APIs/types/functions:** Types: class TransactionInterimResponse : SMB1Command. Constructors: TransactionInterimResponse. Constants/static metadata: ParametersLength. Fields/properties: none detected. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: SMB1Command.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
