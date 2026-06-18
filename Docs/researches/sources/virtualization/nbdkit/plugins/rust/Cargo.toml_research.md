# File Research: sources/virtualization/nbdkit/plugins/rust/Cargo.toml

Cargo manifest for the `nbdkit` Rust binding crate, version `0.3.0`, edition 2021, minimum Rust `1.77`. Metadata identifies it as BSD-2-Clause Rust bindings for creating NBDKit Network Block Device servers.

Runtime dependencies are `bitflags`, `libc`, and optional `nix` socket support; development dependencies include `errno`, `lazy_static`, `memoffset`, and `mockall`. The `ramdisk` example is built as a `cdylib`, matching nbdkit's loadable plugin model.
