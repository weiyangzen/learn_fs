# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Locking/LockType.cs

- **Purpose:** Request to cancel all outstanding lock requests for the specified FID and PID. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 24 lines, 669 bytes. Namespace `SMBLibrary.SMB1`. Primary type `LockType`.
- **Important APIs/types/functions:** Types: enum LockType : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: READ_WRITE_LOCK=0x00, SHARED_LOCK=0x01, OPLOCK_RELEASE=0x02, CHANGE_LOCKTYPE=0x04, CANCEL_LOCK=0x08, LARGE_FILES=0x10.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
