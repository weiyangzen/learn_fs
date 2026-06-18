# sources/security-integrity/cryfs/crates/rustfs/src/common/inode_number.rs

Purpose: typed nonzero inode number wrapper.

Important APIs: `InodeNumber { inode: NonZeroU64 }`, `from_const`, conversions, display, ordering, hashing, and `HandleTrait`.

Control flow and state: like `FileHandle`, it provides monotonic increment and range iteration over nonzero values.

Dependencies and integration: used by low-level API replies, inode list, handle forest, tests, and mock helpers. Constants such as `FUSE_ROOT_ID` and `DUMMY_INO` are built from it.

Risks and tests: invalid zero values are unrepresentable. Overflow and conversion assumptions are handled by assertions/unwraps in callers. Stable inode behavior depends on `InodeList`, not this wrapper alone.
