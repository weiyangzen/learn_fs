# sources/object-store/rustfs/crates/madmin/src/lib.rs

Purpose: crate entry point for RustFS admin data contracts. It declares the module layout and chooses which modules are flattened into the public prelude.

Important APIs/types/functions: exposes modules `group`, `heal_commands`, `health`, `info_commands`, `metrics`, `net`, `policy`, `service_commands`, `site_replication`, `trace`, `user`, and `utils`. Public glob re-exports are limited to `group::*`, `info_commands::*`, `policy::*`, `site_replication::*`, and `user::*`.

Control flow: none. Compilation and public API shape are the behavior. Consumers can access all modules by path, but only selected schema families are available directly as `madmin::TypeName`.

State and persistence: no runtime state or persistence.

Dependencies/integration: integrates all sibling modules into one crate namespace. The limited re-export set matters for downstream imports: metrics, trace, service commands, health, net, and utils require module-qualified access unless separately re-exported elsewhere.

Risks: glob re-exports can create future name collisions between group/info/policy/site_replication/user schemas. Adding a new module is not enough to make its types prelude-visible; this file must be updated deliberately.

Test signals: no local tests. Coverage is indirect through compilation and tests in re-exported modules such as `info_commands.rs` and `user.rs`.
