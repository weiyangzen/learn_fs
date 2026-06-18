# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/OpenResults.cs

- **Purpose:** Defines OpenResults for the packed SMB1 enum/bitfield structure layer. It is part of the packed SMB1 enum/bitfield structure surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 52 lines, 1454 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpenResults`.
- **Important APIs/types/functions:** Types: struct OpenResults. Constructors: OpenResults. Constants/static metadata: Length. Fields/properties: OpenResult, OpLockGranted. Methods/overrides: WriteBytes, Read.
- **Control flow:** Constructors decode packed bytes or integers into fields; WriteBytes and conversion helpers repack those fields into the SMB wire layout.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality.
