# sources/object-store/rustfs/crates/iam/Cargo.toml

This manifest defines the `rustfs-iam` crate, described as RustFS identity and access management for users, roles, and permissions. It inherits workspace edition/license/repository/rust-version/version/homepage/lints and disables doctests for the library.

Dependencies show IAM's integration surface: RustFS credentials, config, ECStore persistence, policy, crypto, admin models, utilities, and IO metrics; Tokio, async traits, time/serde, JSON, `arc-swap`, futures, base64, JWTs, tracing, `moka`, `reqwest`, `openidconnect`, HTTP, and URL parsing. Dev dependencies include `pollster`, `serial_test`, and `temp-env`.

The manifest indicates IAM is both persistent and network/OIDC-aware, not just an in-memory policy engine. Version compatibility is workspace-controlled, and disabled doctests reduce documentation validation. `arc-swap` directly supports the cache snapshot architecture in `src/cache.rs`.
