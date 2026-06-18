<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.github/workflows/ci.yml -->
# sources/security-integrity/cryfs/.github/workflows/ci.yml

**Purpose**
This workflow defines CryFS continuous integration across operating systems, toolchains, feature modes, formatting, documentation, and coverage.

**Important APIs, Types, And Functions**
The `test` job runs `cargo test` over macOS 14/15/15-intel/26 and Ubuntu 22.04/24.04, debug/release, default/no-default features, and stable/nightly/MSRV 1.95. `crates_individually_testable` runs `cargo check` per crate over targets and feature modes. Additional jobs run rustfmt check, `cargo doc` with warnings denied, and `cargo llvm-cov` upload to Codecov. Concurrency cancels superseded runs.

**Control Flow**
Each job checks out the repository, installs OS dependencies such as FUSE packages or macFUSE, installs a Rust toolchain via a pinned `dtolnay/rust-toolchain` action, then runs cargo commands. macOS test commands skip FUSE mount tests and flaky example.com reqwest smoke tests.

**State And Persistence**
CI state includes build caches/artifacts and Codecov upload output; no project runtime state is persisted.

**Dependencies And Integration Points**
The workflow depends on GitHub Actions runners, apt/brew, macFUSE, rustup toolchains, `cargo-llvm-cov`, Codecov, and all workspace crates.

**Risks**
The matrix is large and expensive. Comments note disabled clippy/readme sync jobs and missing release coverage in per-crate checks. Network and FUSE behavior on hosted macOS are explicitly fragile.

**Test Signals**
This is the primary quality gate: workspace tests, per-crate compilability, formatting, dead doc links, and coverage all feed CI status.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.github/workflows/ci.yml -->
