# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/symlink.rs

Purpose: object interface for symbolic links.

Important APIs: `Symlink::into_node` and async `target`.

Control flow and state: adapters downcast a node with `as_symlink`, call `target`, and return the string to readlink callers.

Dependencies and integration: used by high-level and low-level readlink handling and symlink creation paths.

Risks and tests: target is an unconstrained string; comments elsewhere note the lack of a relative-or-absolute path type. Implementations must preserve target bytes/encoding semantics.
