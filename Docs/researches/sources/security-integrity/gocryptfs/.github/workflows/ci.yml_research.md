# sources/security-integrity/gocryptfs/.github/workflows/ci.yml

Purpose: This GitHub Actions workflow builds, tests, and statically checks gocryptfs across supported Go and platform configurations.

Important APIs and jobs: Jobs check out the repository, install dependencies, run build scripts, run Go tests, lint or static-check code, and exercise OpenSSL/non-OpenSSL build variants.

Control flow and state: Triggered by pushes and pull requests; matrix jobs create independent build/test state in GitHub runners.

Dependencies and integration points: Integrates `build.bash`, `build-without-openssl.bash`, `test.bash`, Go modules, FUSE/kernel prerequisites where available, and action-version management.

Risks and test signals: FUSE tests can be runner-sensitive, while pure Go tests should be deterministic. Signals include successful default and no-OpenSSL builds, unit tests, static analysis, and shell/script checks.
