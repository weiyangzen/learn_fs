# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSubcommand.cs

- **Purpose:** Defines NTTransactSubcommand for the NT transaction subcommand layer. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 58 lines, 2005 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactSubcommand`.
- **Important APIs/types/functions:** Types: class NTTransactSubcommand. Constructors: NTTransactSubcommand. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetSetup, GetParameters, GetData, GetSubcommandRequest. Dispatch cases: NTTransactSubcommandName.NT_TRANSACT_CREATE, NTTransactSubcommandName.NT_TRANSACT_IOCTL, NTTransactSubcommandName.NT_TRANSACT_SET_SECURITY_DESC, NTTransactSubcommandName.NT_TRANSACT_NOTIFY_CHANGE, NTTransactSubcommandName.NT_TRANSACT_QUERY_SECURITY_DESC.
- **Control flow:** A static dispatcher validates setup length or subcommand id and instantiates the concrete request parser, otherwise raising InvalidDataException. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** invalid setup or command values raising InvalidDataException, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** InvalidDataException.
