# sources/sync-backup/restic/internal/fs/node_unix.go

Purpose: Unix ownership and generic-attribute hooks.

Important APIs: `lchown`, `nodeRestoreGenericAttributes`, and `nodeFillGenericAttributes`.

Control flow and state: `lchown` chooses numeric UID/GID or resolves names via caches, then calls `os.Lchown`. Generic attribute restore delegates unknown-attribute warnings to `data.HandleAllUnknownGenericAttributesFound`; fill is no-op.

Dependencies and integration: Used by `NodeRestoreMetadata` on non-Windows targets.

Risks: Name-based ownership fallback returns zero for unknown users/groups, which can map to root if called with unresolved names. Unix generic attributes are currently not persisted except unknown-warning handling.

Test signals: `node_unix_test.go` covers ownership by numeric IDs and by names.
