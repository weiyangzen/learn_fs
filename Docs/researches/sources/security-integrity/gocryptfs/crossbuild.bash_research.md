# sources/security-integrity/gocryptfs/crossbuild.bash

Purpose: This script verifies gocryptfs builds across supported `GOOS`/`GOARCH` combinations.

Important APIs and steps: It defines a build helper that compiles with `without_openssl`, runs package test compilation where appropriate, and invokes it for Linux, Darwin, and FreeBSD architectures including ARM variants.

Control flow and state: It sets environment variables per target and discards binaries to `/dev/null`. State is limited to Go build cache and test compilation artifacts.

Dependencies and integration points: Used by maintainers/CI to prevent portability regressions in pure-Go paths.

Risks and test signals: Cross-compilation can miss runtime FUSE/platform issues but catches compile-time portability. Signals are successful builds for all listed targets and selected test compilation.
