# File Research: sources/virtualization/nbdkit/plugins/rust/clippy.sh

Clippy wrapper for the Rust binding crate. It requires `cargo-clippy`, then runs Clippy across all features and all targets with warnings denied.

It explicitly allows `clippy::declare_interior_mutable_const` because older Clippy versions, including Debian 12's, warn incorrectly about `thread_local!` internals. This keeps CI compatible with the crate's supported toolchain range.
