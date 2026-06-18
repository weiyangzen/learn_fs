# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/SecurityMode.cs

- **Purpose:** If clear, the server supports only Share Level access control. If set, the server supports only User Level access control. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 23 lines, 881 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SecurityMode`.
- **Important APIs/types/functions:** Types: enum SecurityMode : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: UserSecurityMode=0x01, EncryptPasswords=0x02, SecuritySignaturesEnabled=0x04, SecuritySignaturesRequired=0x08.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
