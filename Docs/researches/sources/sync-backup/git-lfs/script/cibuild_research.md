# sources/sync-backup/git-lfs/script/cibuild

Purpose: top-level CI build and validation script for Git LFS.

Important steps: unsets most `GIT*`/`GITHUB*` variables, detects Windows-style environments, installs `scutiger-lfs`, installs `goimports`, runs `make` and `make test`, reruns Git package tests with `GIT_TRACE=1`, runs shell integration tests under `t/`, checks trailing whitespace, runs formatting, and asserts a clean git status.

Control flow: fail-fast bash script. It builds tool dependencies first, runs Go tests, then integration tests, then repository hygiene gates.

State/persistence behavior: installs tools into `t/scutiger` and `$GOPATH/bin`, builds binaries, cleans integration test state, formats files in place, and reads git status.

Dependencies/integration: depends on cargo, Go toolchain, make, prove, bash, and the `t/Makefile` integration test harness.

Risks: `go install ...@latest` can introduce toolchain/network variability. Formatting in place means local modifications are expected if formatting drifts. Environment stripping must preserve required hash settings.

Test signals: CI success means Go unit tests, Git-trace leakage checks, integration tests, whitespace, formatting, and clean tree all pass.
