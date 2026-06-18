# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeDisconnectRequest.cs

- **Purpose:** SMB_COM_TREE_DISCONNECT Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 35 lines, 927 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeDisconnectRequest`.
- **Important APIs/types/functions:** Types: class TreeDisconnectRequest : SMB1Command. Constructors: TreeDisconnectRequest. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: CommandName.SMB_COM_TREE_DISCONNECT.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TREE_DISCONNECT to the message layer.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
