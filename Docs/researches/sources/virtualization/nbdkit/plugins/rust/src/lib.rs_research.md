# File Research: sources/virtualization/nbdkit/plugins/rust/src/lib.rs

Main Rust binding crate for writing nbdkit plugins. It defines `Error`, `Result`, NBD flags, cache/FUA/thread-model enums, extent types, `ExtentHandle`, and the central `Server` trait whose required callbacks are `name`, `open`, `get_size`, and `read_at`, with many optional callbacks modeled as default `unimplemented!()` methods.

The `ffi` module contains C ABI trampolines that downcast opaque handles back to boxed `dyn Server` trait objects, translate raw buffers into Rust slices, convert raw flags with `bitflags`, call trait methods, and propagate Rust errors through `nbdkit_error` plus `nbdkit_set_error`. `Builder::into_ptr` constructs the nbdkit `Plugin` struct, installs selected optional callbacks based on `plugin!` macro arguments, stores static method pointers in global slots, and leaks the plugin table for nbdkit ownership.

The crate exposes safe-ish wrappers for nbdkit helpers such as debug logging, hexdump/hexdiff, export name lookup, stdio/TLS checks, peer name lookup with the optional `nix` feature, shutdown/disconnect, parse helpers, instance name, and timestamp. Limitations are explicit in the plugin struct: list exports, default export, export description, and cleanup fields exist but are not implemented by these bindings.

The embedded tests, gated around mocked C symbols where needed, verify peer-name conversion for IPv4/IPv6/Unix sockets and error behavior. Important integration risk centers on unsafe global initialization and raw FFI pointer lifetimes, which are intentionally constrained by a one-time `plugin!` registration model.
