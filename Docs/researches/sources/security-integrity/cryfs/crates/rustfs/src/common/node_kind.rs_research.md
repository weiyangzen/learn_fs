# sources/security-integrity/cryfs/crates/rustfs/src/common/node_kind.rs

Purpose: compact enum for directory entry kind.

Important APIs: `NodeKind::{Dir, File, Symlink}`.

Control flow and state: stateless enum used for listing and mode classification.

Dependencies and integration: `Mode::node_kind` returns this value; `DirEntry` stores it; tests parameterize over it.

Risks and tests: special files/devices are not represented here despite object API having `Device` and high-level `mknod`; this constrains directory listing expressiveness.
