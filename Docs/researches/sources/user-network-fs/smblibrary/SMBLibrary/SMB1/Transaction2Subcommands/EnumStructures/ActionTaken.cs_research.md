# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/ActionTaken.cs

- **Purpose:** Defines protocol constants for LockStatus. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 34 lines, 1029 bytes. Namespace `SMBLibrary.SMB1`. Primary type `LockStatus`.
- **Important APIs/types/functions:** Types: enum LockStatus : byte, struct ActionTaken. Constructors: ActionTaken. Constants/static metadata: none. Fields/properties: OpenResult, LockStatus. Methods/overrides: WriteBytes. Enum values: NoOpLockWasRequestedOrGranted=0x00, OpLockWasRequestedAndGranted=0x01.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
