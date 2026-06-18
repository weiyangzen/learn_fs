# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/OpenMode.cs

- **Purpose:** Defines protocol constants for CreateFile. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 57 lines, 1586 bytes. Namespace `SMBLibrary.SMB1`. Primary type `CreateFile`.
- **Important APIs/types/functions:** Types: enum CreateFile : byte, enum FileExistsOpts : byte, struct OpenMode. Constructors: OpenMode. Constants/static metadata: Length. Fields/properties: FileExistsOpts, CreateFile. Methods/overrides: WriteBytes, Read. Enum values: ReturnErrorIfNotExist=0x00, CreateIfNotExist=0x01, ReturnError=0x00, Append=0x01, TruncateToZero=0x02.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
