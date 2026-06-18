# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/mod.rs

## Scope

Shared preserialization data model for passthrough migration preparation.

## APIs Covered

- Submodules: `file_handles`, `find_paths`, `proc_paths`.
- `InodeMigrationInfo`: prepared inode location plus optional verification file handle.
- `InodeLocation`: root node, path, or file handle.
- `HandleMigrationInfo`: currently `OpenInode { flags }`.

## Behavior

- `InodeMigrationInfo::new()` chooses location type from `MigrationMode`.
- `new_internal()` optionally attaches a verification `SerializableFileHandle` when `migration_verify_handles` is enabled.
- `new_root()` records root-node migration info without path data.
- `for_each_strong_reference()` exposes strong parent references embedded in path locations so lifetime/refcount handling can be balanced.
- `has_path()` identifies migration info that must be invalidated or updated on rename/unlink.
- `check_path_presence()` delegates validation to path-backed locations.
- `HandleMigrationInfo::new()` strips `O_CREAT`, `O_EXCL`, and `O_TRUNC` from preserved open flags before migration.

## Invariants

Root location is destination-configured, path locations carry parent references, and file-handle locations do not. Handle reopen flags must not recreate, exclusively create, or truncate files after migration.
