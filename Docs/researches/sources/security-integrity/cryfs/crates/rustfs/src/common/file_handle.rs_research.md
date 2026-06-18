# sources/security-integrity/cryfs/crates/rustfs/src/common/file_handle.rs

Purpose: typed nonzero FUSE file-handle wrapper used for open files and directory handles.

Important APIs: `FileHandle { handle: NonZeroU64 }`, `from_const`, derived `From`/`Into`, display, ordering, hashing, and `HandleTrait` implementation. `MIN` is 1 and `MAX` is `u64::MAX`.

Control flow and state: `incremented` constructs the next nonzero value. `range` iterates the numeric range and unwraps `NonZeroU64`; the range starts from valid nonzero handles.

Dependencies and integration: used by `OpenFileList`, `DirCache` through `OpenDirHandle`, high/low API response structs, and descriptor-related errors. Re-exported as a public common type.

Risks and tests: the type prevents zero handles, but several call sites unwrap numeric conversions and assume no overflow. `HandlePool` asserts before incrementing past `MAX`, so exhaustion panics rather than returning an error.
