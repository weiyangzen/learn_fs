# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/AccessModeOptions.cs

- **Purpose:** Write-through mode. If this flag is set, then no read ahead or write behind is allowed on this file or device. When the response is returned, data is expected to be on the disk or device. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 97 lines, 3010 bytes. Namespace `SMBLibrary.SMB1`. Primary type `AccessMode`.
- **Important APIs/types/functions:** Types: enum AccessMode : byte, enum SharingMode : byte, enum ReferenceLocality : byte, enum CachedMode : byte, enum WriteThroughMode : byte, struct AccessModeOptions. Constructors: AccessModeOptions. Constants/static metadata: Length. Fields/properties: AccessMode, SharingMode, ReferenceLocality, CachedMode, WriteThroughMode. Methods/overrides: WriteBytes, Read. Enum values: Read=0x00, Write=0x01, ReadWrite=0x02, Execute=0x03, Compatibility=0x00, DenyReadWriteExecute=0x01, DenyWrite=0x02, DenyReadExecute=0x03, DenyNothing=0x04, Unknown=0x00, Sequential=0x01, Random=0x02, RandomWithLocality=0x03, CachingAllowed=0x00, DoNotCacheFile=0x01, Disabled=0x00, WriteThrough=0x01.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
