# sources/security-integrity/cryfs/crates/rustfs/src/common/num_bytes.rs

Purpose: typed byte-count and offset wrapper.

Important APIs: `NumBytes(u64)` with display/from/into, `ZERO`, conversions to `usize`, `as_usize`, `checked_add`, and `Sub`.

Control flow and state: immutable numeric wrapper. `as_usize` and `TryFrom<NumBytes> for usize` return `FsError::InvalidOperation` when the value does not fit.

Dependencies and integration: used for file size, offsets, read/write lengths, xattr sizes, block sizes, and stat structures.

Risks and tests: `Sub` directly subtracts and will panic on underflow in debug builds or wrap depending on compilation settings if unchecked. Several callers unwrap conversions from `usize` to `u64`.
