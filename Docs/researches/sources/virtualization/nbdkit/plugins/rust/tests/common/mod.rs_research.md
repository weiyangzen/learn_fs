# File Research: sources/virtualization/nbdkit/plugins/rust/tests/common/mod.rs

Shared test support for Rust binding integration tests. It defines thread-local captures for nbdkit error messages and errno, a mutex protecting mock static expectations, a `MockServer` implementing the full `Server` trait via `mockall`, and a mocked `nbdkit_add_extent`.

Also supplies replacement C symbols for `nbdkit_error`, `nbdkit_set_error`, and `nbdkit_add_extent` so Rust ABI trampolines can be tested without a real nbdkit binary. The `Fixture` struct bundles the mock handle pointer, generated plugin table reference, and opaque handle used by callback tests.
