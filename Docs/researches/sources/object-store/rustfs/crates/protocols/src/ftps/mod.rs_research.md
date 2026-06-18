# sources/object-store/rustfs/crates/protocols/src/ftps/mod.rs

Purpose: This is the FTPS module declaration file.

Important APIs and types: It exposes `config`, `driver`, and `server` submodules. Public crate-level re-exports are handled in `lib.rs`, not here.

Control flow: There is no runtime control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: The module enables feature-gated `crate::ftps::*` imports when the `ftps` feature is compiled. `server` depends on both `config` and `driver`; consumers typically reach `FtpsConfig` and `FtpsServer` through `lib.rs`.

Risks: Removing or renaming a module here breaks feature builds and crate re-exports. There is no logic-specific risk.

Test signals: Compilation of the FTPS feature is the relevant signal.
