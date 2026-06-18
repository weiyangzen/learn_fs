<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/lib.rs -->
# sources/storage-engines/tikv/components/error_code/src/lib.rs

Purpose: this is the root of the `error_code` crate. It defines the shared `ErrorCode` representation, the `ErrorCodeExt` trait, the `UNKNOWN` fallback, all public domain modules, and the macro used by every module to declare constants.

Important APIs and types: `ErrorCode` is a `Copy` struct with static `code`, `description`, and `workaround` fields, and implements `Display` by printing the code. `ErrorCodeExt` defines `fn error_code(&self) -> ErrorCode` for downstream error types. `define_error_codes!` takes a prefix and `NAME => (suffix, description, workaround)` entries, emits `pub const` values with `concat!($prefix, $suffix)`, and creates a module-local `ALL_ERROR_CODES: Vec<ErrorCode>` in `lazy_static!`.

Control flow and state: most behavior is compile-time macro expansion plus runtime lazy vector initialization. The root exports modules including `backup_stream`, `causal_ts`, `cloud`, `codec`, `coprocessor`, `encryption`, `engine`, `pd`, `raft`, `raftstore`, `sst_importer`, and `storage`. The crate uses `#![feature(min_specialization)]`, so it assumes a nightly toolchain.

Dependencies and integration points: `lazy_static` powers catalog vectors; `kvproto` and `raft` are used by submodules for conversion implementations; `tikv_alloc` installs TiKV allocator hooks. Other crates integrate by importing constants or implementing/using `ErrorCodeExt`.

Risks: `UNKNOWN` has code `KV:Unknown` with empty metadata, making it a coarse fallback. The macro creates a fixed `Vec`, not a sorted or deduplicated catalog, so duplicate constants would only be caught by external review. Generated catalogs can diverge from exported modules because `bin.rs` maintains its own module list.

Test signals: `test_define_error_code` verifies that the macro concatenates prefixes and suffixes correctly and emits public constants with expected metadata. It does not test `ALL_ERROR_CODES` contents or duplicate handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/lib.rs -->
