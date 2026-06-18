# sources/security-integrity/cryfs/crates/rustfs/src/common/mode.rs

Purpose: typed POSIX mode wrapper combining file-type bits and permission bits.

Important APIs: `Mode(u32)` with constants for file types and rwx permissions, `default_const`, `as_u32`, node-kind predicates/conversion, flag add/remove methods, `BitAnd`, `BitOr`, `Not`, `Display`, and custom `Debug`.

Control flow and state: immutable value object. File-type helpers clear previous type bits before adding dir/file/symlink flags, preventing mixed type flags when using provided methods. Permission methods OR or AND bits.

Dependencies and integration: used in `NodeAttrs`, create/mkdir/mknod/setattr/open APIs, tests, and backend adapters. `mkdir` tests verify directory flag behavior and umask interaction.

Risks and tests: direct `From<u32>` can construct inconsistent modes; callers need to use helpers or validate. Debug formatting can aid tests. Several TODOs ask for broader mode semantics.
