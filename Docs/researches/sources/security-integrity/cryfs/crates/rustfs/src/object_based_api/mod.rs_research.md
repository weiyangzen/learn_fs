# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/mod.rs

Purpose: public module facade for object-based RustFS support.

Important APIs: re-exports object traits, `FUSE_ROOT_ID`, high-level and low-level adapters, backend wrappers, and backend config/mount types.

Control flow and state: no runtime behavior. Feature gates control adapter and backend availability.

Dependencies and integration: this is the main entry point for users implementing `Device` and mounting it through RustFS.

Risks and tests: feature-specific exports can alter public API. It exposes low-level root inode only when fuser utilities are built.
