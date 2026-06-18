<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.cargo/config.toml -->
# sources/security-integrity/cryfs/.cargo/config.toml

**Purpose**
This Cargo configuration improves developer debug-build performance for CPU-heavy cryptographic dependencies.

**Important APIs, Types, And Functions**
It sets `[profile.dev.package.<name>] opt-level = 3` for `scrypt`, `aead`, `aes-gcm`, `chacha20poly1305`, and `openssl`.

**Control Flow**
Cargo applies these package-specific optimization levels when compiling in the dev profile. Project crates remain at the normal dev profile settings while selected dependencies are optimized.

**State And Persistence**
The file affects local and CI build artifacts in Cargo target directories. It stores no runtime state.

**Dependencies And Integration Points**
It integrates with the root Cargo workspace and the crypto dependency set declared in `Cargo.toml`.

**Risks**
Optimized dependencies can make debug stepping into those crates harder and may hide performance issues in project code. Keeping this list in sync with active crypto dependencies is manual.

**Test Signals**
CI and local `cargo test`/`cargo build` exercise this config implicitly when Cargo reads the workspace.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.cargo/config.toml -->
