## sources/security-integrity/encfs/src/crypto/mod.rs

Purpose: Module declaration hub for EncFS crypto code.

Important APIs and modules: exposes `aead`, `block`, `file`, and `ssl` submodules. Control flow is compile-time module inclusion only; it defines the namespace used by the rest of the crate.

State and persistence: None directly. Dependencies are the corresponding Rust source files. Integration: callers import `crate::crypto::aead` for V7 key wrap, `block` for block modes/layout, `file` for file encode/decode, and `ssl` for cipher primitives/KDFs. Risks are low, but adding/removing modules here changes public internal paths across the crate and can break config, filesystem, and fuzz code.
