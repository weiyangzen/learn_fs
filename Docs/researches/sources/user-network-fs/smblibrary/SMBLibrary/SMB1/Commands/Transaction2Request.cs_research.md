# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2Request.cs

- **Purpose:** SMB_COM_TRANSACTION2 Request The SMB_COM_TRANSACTION2 request format is similar to that of the SMB_COM_TRANSACTION request except for the Name field. The differences are in the subcommands supported, and in the purposes and usages of some. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 37 lines, 1183 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2Request`.
- **Important APIs/types/functions:** Types: class Transaction2Request : TransactionRequest. Constructors: Transaction2Request. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION2.
- **Control flow:** It reuses the generic transaction request parse/serialize path and changes only the SMB command discriminator.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionRequest.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION2 to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
