# File Research: sources/os/linux/linux/mm/kasan/kasan_test_rust.rs

Rust helper crate for the KASAN KUnit suite.

Exports:
- `#[no_mangle] extern "C" fn kasan_test_rust_uaf() -> u8`

Behavior:
- Allocates a `KVec<u8>`.
- Pushes 4096 bytes of `0x42`.
- Takes a raw mutable pointer to element 2048.
- Drops the vector.
- Unsafely dereferences the stale pointer.

Purpose:
This intentionally creates a Rust use-after-free through `unsafe` code so the C KUnit suite can verify that Rust code is sanitized by KASAN. The matching C test is `rust_uaf()` in `kasan_test_c.c`, gated by `CONFIG_RUST`.
