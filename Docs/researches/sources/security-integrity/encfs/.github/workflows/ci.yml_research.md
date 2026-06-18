## sources/security-integrity/encfs/.github/workflows/ci.yml

Purpose: GitHub Actions workflow for Rust CI on pushes and pull requests to `master`. It performs lint, release build, release tests, and live FUSE mount tests.

Important APIs and functions: workflow triggers, `CARGO_TERM_COLOR`, `actions/checkout@v4`, apt installation of `fuse libfuse-dev pkg-config`, `modprobe fuse`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --release`, `cargo test --release`, and ignored live mount test command with `ENCFS_LIVE_TESTS=1`.

State and persistence: Ephemeral CI runner state and loaded kernel module. Dependencies are Ubuntu latest, FUSE device/module support, Rust default toolchain, and system libfuse headers. Integration is primary Linux validation. Risks: `modprobe fuse` is continue-on-error, so live tests may fail later depending on runner capabilities; clippy with `-D warnings` makes lint drift fail builds.
