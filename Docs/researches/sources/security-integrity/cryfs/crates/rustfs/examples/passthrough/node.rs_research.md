# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/node.rs

Purpose: Implements passthrough node metadata and type conversion operations.

Important APIs/types/functions: `PassthroughNode::new`, private `chmod`, `chown`, `truncate`, and `utimens`, and the `Node` impl for type conversions, `getattr`, `setattr`, and test-only fsync.

Control flow: `getattr` uses `symlink_metadata` to avoid following symlinks. `setattr` applies chmod, chown, truncate, and utimens in sequence, then returns fresh attrs. Unix metadata operations that can block use `spawn_blocking`.

State and persistence behavior: mutates host filesystem metadata and file size. No additional state is stored.

Dependencies and integration points: type conversion returns passthrough dir/file/symlink wrappers. Uses error extensions and metadata/time conversion utilities.

Risks: `chmod` builds `self.path.clone().push_all(&self.path)`, which appears to duplicate the path and is likely a bug. `as_file/as_dir/as_symlink` TODOs note they do not validate actual node type. ctime setting asserts.

Test signals: tests should catch chmod path handling, wrong-type conversions, symlink-no-follow metadata behavior, truncate, chown, and utimens.
