# sources/storage-engines/raft-engine/.github/workflows/rust.yml

## Purpose
Defines raft-engine's GitHub Actions Rust CI for linting, tests, feature matrix coverage, and Codecov upload.

## Important APIs, Types, And Functions
The workflow has `stable` and `coverage` jobs. It installs Rust 1.85.0 with rustfmt, clippy, and rust-src for stable validation, and nightly-2026-01-30 with llvm-tools-preview for coverage. It uses `actions/checkout@v2`, `actions-rs/toolchain@v1`, `Swatinem/rust-cache@v1`, `grcov`, and `codecov/codecov-action@v3`.

## Control Flow
The workflow runs on pushes except `dependabot/**` branches and on pull requests except docs/OWNERS-only changes. The stable job runs `make clippy` and `make test` with `WITH_STABLE_TOOLCHAIN=force`. The coverage job waits for stable, runs `make test_matrix` under coverage instrumentation, converts `.profraw` data to lcov with grcov, and uploads `coverage.lcov`.

## State And Persistence Behavior
No production state is changed. CI cache state is shared by OS/toolchain key, and Codecov receives coverage artifacts. Environment variables set cargo color, backtraces, verbose cargo output, and coverage flags.

## Dependencies And Integration Points
Integrates with the repository `Makefile`, Cargo workspace, feature flags, failpoint tests, Codecov config, Rust toolchains, and GitHub secrets for `CODECOV_TOKEN`.

## Risks And Edge Cases
The checkout ref assumes pull_request context; push events without that field may rely on GitHub expression behavior. Actions versions are older. Coverage depends on nightly availability and grcov installation. Path ignores prevent CI from running for markdown-only changes, which is intentional but can miss generated docs that affect examples.

## Test Signals
Signals are clippy success, stable tests, failpoints test pass, nightly feature matrix pass, grcov success, and Codecov status checks with configured thresholds.
