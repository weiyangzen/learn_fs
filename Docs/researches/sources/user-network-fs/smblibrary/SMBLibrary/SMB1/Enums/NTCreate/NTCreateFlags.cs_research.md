# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/NTCreateFlags.cs

- **Purpose:** If set, the client requests an exclusive OpLock. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 20 lines, 554 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTCreateFlags`.
- **Important APIs/types/functions:** Types: enum NTCreateFlags : uint. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NT_CREATE_REQUEST_OPLOCK=0x00000002, NT_CREATE_REQUEST_OPBATCH=0x00000004, NT_CREATE_OPEN_TARGET_DIR=0x00000008, NT_CREATE_REQUEST_EXTENDED_RESPONSE=0x00000010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
