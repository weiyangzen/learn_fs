# sources/security-integrity/fscrypt/.github/workflows/ci.yml

Purpose: GitHub Actions CI definition for `fscrypt`, covering Go builds, 32-bit build, integration tests, cgroup integration, CLI tests, generated-code checks, formatting, and linting.

Important jobs: `build` runs `make` across Go 1.23, 1.24, and 1.25. `build-32bit` builds with `CGO_ENABLED=1 GOARCH=386` and i386 PAM headers. `run-integration-tests` installs filesystem/key dependencies, runs `make test-setup`, links keyrings with `keyctl link @u @s`, then runs `make test` and teardown. `test-cgroup-integration` builds a package test binary and runs it inside Docker with CPU/memory constraints. `run-cli-tests` installs `expect` and runs `make cli-test`. `generate-format-and-lint` runs `make tools`, `make gen`, `make format`, `make lint`, and file-change checks.

Control flow: workflow triggers on pushes and pull requests to `master`. Jobs run independently on Ubuntu latest with checkout and setup-go. A commented architecture matrix documents why qemu-based integration is disabled.

State and persistence: CI creates build outputs, loopback test filesystems, Docker containers, generated files, and tool binaries within runner workspace; no repo state persists except job artifacts/logs.

Dependencies and integration points: depends on GitHub Actions, apt packages (`libpam0g-dev`, `e2fsprogs`, `keyutils`, `shellcheck`, etc.), Docker, Go toolchain, Makefile targets, kernel fscrypt/keyctl support.

Risks: `actions/setup-go@v2` is old even while using new Go versions. Integration jobs require privileged kernel features that may shift on hosted runners. `make test-teardown` is not guarded with `always()`, so failure before teardown may leave runner-local mounts until VM cleanup.

Test signals: defines the authoritative CI coverage expected for fscrypt source changes.
