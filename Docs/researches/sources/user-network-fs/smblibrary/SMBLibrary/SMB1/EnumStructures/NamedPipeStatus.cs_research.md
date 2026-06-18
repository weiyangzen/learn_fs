# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/NamedPipeStatus.cs

- **Purpose:** SMB_NMPIPE_STATUS. It is part of the packed SMB1 enum/bitfield structure surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 97 lines, 3000 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ReadMode`.
- **Important APIs/types/functions:** Types: enum ReadMode : byte, enum NamedPipeType : byte, enum Endpoint : byte, enum NonBlocking : byte, struct NamedPipeStatus. Constructors: NamedPipeStatus. Constants/static metadata: Length. Fields/properties: ICount, ReadMode, NamedPipeType, Endpoint, NonBlocking. Methods/overrides: WriteBytes, ToUInt16, Read. Enum values: ByteMode=0x00, MessageMode=0x01, ByteModePipe=0x00, MessageModePipe=0x01, ClientSideEnd=0x00, ServerSideEnd=0x01, Block=0x00, DoNotBlock=0x01.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
