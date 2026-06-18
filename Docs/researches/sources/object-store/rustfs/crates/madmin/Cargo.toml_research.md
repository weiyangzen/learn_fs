<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/Cargo.toml -->
# sources/object-store/rustfs/crates/madmin/Cargo.toml

Purpose: `Cargo.toml` defines the `rustfs-madmin` crate, which provides management/admin data structures and APIs for RustFS.

Important APIs/types/functions: package metadata names the crate `rustfs-madmin`, inherits edition/license/repository/rust-version/version/homepage from the workspace, and describes management/admin tooling with docs.rs documentation. It disables doctests for the library. Runtime dependencies are workspace versions of `chrono`, `humantime`, `hyper`, `serde`, `serde_json`, and `time`; dev dependency is `rmp-serde`.

Control flow: no runtime control flow exists. Cargo uses this manifest to compile the crate and resolve workspace dependency versions/lints.

State and persistence behavior: no application state is stored here. Dependency choices influence serialization formats and API model support in the Rust source files.

Dependencies and integration points: `serde`, `serde_json`, and `time` are directly used by the listed `group.rs`, `heal_commands.rs`, and `health.rs` files. `rustfs-madmin` types are consumed by object-store/ecstore healing and peer APIs, especially `HealResultItem`, `HealDriveInfo`, group descriptions, and health payloads.

Risks: disabling doctests means examples in documentation will not be validated. Workspace-inherited versions centralize compatibility but can introduce changes crate-wide. `hyper` is listed even though these specific model files are mostly serde data structures; unused dependency risk depends on other madmin modules.

Test signals: crate tests in individual source modules validate serde behavior for group and health models. Build/test coverage should include the whole workspace because madmin structs are serialized across admin and peer APIs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/Cargo.toml -->
