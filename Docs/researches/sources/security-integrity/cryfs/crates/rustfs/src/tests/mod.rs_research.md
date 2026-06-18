# sources/security-integrity/cryfs/crates/rustfs/src/tests/mod.rs

Purpose: test module root.

Important APIs: declares `utils` and `mkdir`.

Control flow and state: no runtime behavior.

Dependencies and integration: included by `lib.rs` under `cfg(test)`.

State and persistence behavior: this module does not own test state; it wires the helper harness and mkdir tests into the crate test build. The actual persistent side effects happen in mounted temporary filesystems created by `utils::Runner`.

Risks and tests: only listed test suite here is mkdir plus utilities, indicating current test coverage is narrow for the broader filesystem API. The absence of additional module declarations means many adapters, inode-list invariants, xattr paths, readdir offsets, and error mappings are not directly exercised from this test root.
