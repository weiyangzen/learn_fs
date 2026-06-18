# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/symlink.rs

Purpose: Implements in-memory symlink nodes.

Important APIs/types/functions: `SymlinkInode` stores metadata and target string. `InMemorySymlinkRef` supports creation, cloning, metadata, setattr, and target access. The `Symlink` trait impl returns the target.

Control flow: symlink read simply clones the stored target. Setattr rejects size changes and mutates metadata fields through the shared helper.

State and persistence behavior: target and attrs are held in an `Arc<Mutex<_>>` and never persisted.

Dependencies and integration points: used by in-memory directories and node dispatch; complements file and dir implementations.

Risks: size changes assert rather than returning an error. Metadata timestamps are approximate. Target is not validated beyond being a Rust string.

Test signals: cover target round-trip, wrong size setattr, clone sharing, and metadata updates.
