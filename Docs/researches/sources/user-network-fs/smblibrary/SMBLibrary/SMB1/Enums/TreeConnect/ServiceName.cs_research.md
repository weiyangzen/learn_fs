# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/ServiceName.cs

- **Purpose:** Valid only for request. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 16 lines, 265 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ServiceName`.
- **Important APIs/types/functions:** Types: enum ServiceName. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: DiskShare, PrinterShare, NamedPipe, SerialCommunicationsDevice, AnyType.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
