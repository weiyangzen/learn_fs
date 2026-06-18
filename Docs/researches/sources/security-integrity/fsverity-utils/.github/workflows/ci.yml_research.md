# sources/security-integrity/fsverity-utils/.github/workflows/ci.yml

Purpose: This GitHub Actions workflow builds and tests fsverity-utils across compiler, crypto-library, architecture, and packaging combinations.

Important APIs and jobs: The workflow defines CI jobs for Linux builds, test execution, sparse/static analysis, cross or alternate compiler coverage, dependency setup, and artifact/package checks. It drives `make`, project test scripts, and package manager installs.

Control flow and state: Jobs are event-triggered and mostly stateless, with state limited to the checked-out tree, installed packages, build outputs, and workflow caches if configured. Matrix expansion is the main control-flow mechanism.

Dependencies and integration points: Integrates with the Makefile, `scripts/run-tests.sh`, `scripts/run-sparse.sh`, OpenSSL/BoringSSL or libcrypto variants, Linux headers, and GitHub Actions runners.

Risks and test signals: CI risk centers on host package availability, kernel/fs-verity feature availability, and matrix drift. Signals include successful compile, library tests, CLI tests, sparse checks, and build modes that omit optional OpenSSL features.
