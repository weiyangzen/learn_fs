# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/mod.rs

## Scope

Top-level migration-state module for `PassthroughFs`.

## Structure

- Declares submodules: `deserialization`, `preserialization`, `serialization`, and `serialized`.
- Implements `SerializableFileSystem` for `PassthroughFs`.

## Behavior

- `prepare_serialization()` clears old migration info, enables migration-info tracking, then prepares inode locations using either proc-path reconstruction plus tree-walk fallback or file-handle construction.
- Runs an implicit path check after preserialization to catch races where paths became stale while being recorded.
- `serialize()` disables tracking, optionally confirms paths at switch-over, converts state to serialized V2, clears migration info, and writes bytes to the state pipe.
- `deserialize_and_apply()` reads all bytes from the state pipe and applies either V1 or V2 serialized state.

## Risks

Migration is explicitly best-effort during preparation but strict during final serialization when configured to confirm paths. Cancellation is cooperatively checked by constructors.
