# File Research: sources/virtualization/nbdkit/plugins/rust/tests/bare_bones.rs

Unit tests for a minimal Rust plugin registration using `plugin!(MockServer{})`, with no optional callbacks enabled. Because the binding uses one-time global state, this file has its own process-level plugin initialization path guarded by `Once`.

The fixture sets required static metadata expectations, opens a mocked handle through the generated plugin table, and tests the minimal open/close/get-size path. It also tests `pread` success and error translation, including buffer mutation, errno propagation, and captured error messages through mocked `nbdkit_error`.
