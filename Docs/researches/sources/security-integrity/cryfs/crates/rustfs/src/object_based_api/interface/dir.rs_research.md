# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/dir.rs

Purpose: object interface for directories.

Important APIs: `Dir::into_node`, `entries`, `lookup_child`, `rename_child`, `move_child_to`, `create_child_dir`, `create_child_symlink`, `create_and_open_file`, `remove_child_file_or_symlink`, `remove_child_dir`, and `fsync`.

Control flow and state: trait implementors own directory persistence. Adapters call create methods, often immediately converting returned child objects into nodes or dropping them after collecting attrs. `lookup_child` must return `NodeDoesNotExist` immediately for missing names.

Dependencies and integration: used by device lookup, high-level adapter, low-level adapter, and inode loading. It uses typed path components, modes, uid/gid, open flags, attrs, and `DirEntry`.

Risks and tests: semantics of overwrite, move, and fsync are delegated to implementations. Low-level adapter assumes successful unlink/rmdir means inode forest can be orphaned.
