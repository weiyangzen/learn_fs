# File Research: sources/virtualization/nbdkit/plugins/rust/Makefile.am

Automake integration for the Rust binding crate. It distributes the Cargo manifest, Rust source, tests, scripts, example plugin, README/license/changelog, and POD documentation.

When Rust is available, it builds the release `libnbdkit.rlib`, the release `libramdisk.so` example, and generated Rust documentation through Cargo targets. Test integration runs `cargo-tests.sh`, `test-ramdisk.sh`, and optionally `clippy.sh` under compiler-warning builds; POD tooling conditionally generates `nbdkit-rust-plugin.3`.
