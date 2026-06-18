# sources/security-integrity/cryfs/crates/fsblobstore/src/utils/fs_types.rs

Purpose: Defines local filesystem scalar types used by fsblobstore without depending on `cryfs-rustfs`.

Important APIs/types/functions: `Uid` and `Gid` are `u32` newtypes with binary read/write and conversions. `Mode` is a `u32` bitmask newtype with derive-more bit operators, constructors, node-kind flag checks, and const helpers for setting file/dir/symlink and permission bits.

Control flow: no complex flow. Methods create modified copies or query bit flags.

State and persistence behavior: these values serialize via `binrw` inside directory entries. Mode bit constants include POSIX type bits and basic user/group/other rwx permissions.

Dependencies and integration points: used by `DirEntry`, `DirBlob`, and typed blob APIs. A TODO notes possible unification with rustfs types while avoiding unwanted crate dependencies.

Risks: only add/with helpers are present, not remove helpers for all bits. Incorrect mode construction can fail `DirEntry` validation. Duplicating rustfs types risks semantic drift.

Test signals: tests should cover bit operations, binary round trips, and compatibility with rustfs `Mode` values used at integration boundaries.
