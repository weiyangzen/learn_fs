# File Research: sources/virtualization/nbdkit/plugins/rust/test-ramdisk.sh

End-to-end shell test for the Rust `ramdisk` example plugin. It skips Windows, requires the built release example shared object, and checks availability of runtime tooling such as `nbdinfo` and `nbdsh`.

The test launches nbdkit with the Rust plugin to confirm export discovery, then uses `nbdsh` to write and read back a 4 KiB buffer at offset 16384. A final run enables `hexdump=true` and performs a small write to exercise the Rust `debug_hexdump` wrapper without asserting on the textual debug output.
