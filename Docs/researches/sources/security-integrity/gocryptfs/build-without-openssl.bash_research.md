# sources/security-integrity/gocryptfs/build-without-openssl.bash

Purpose: This script builds gocryptfs without OpenSSL support, forcing the pure-Go crypto path.

Important APIs and steps: It sets `CGO_ENABLED=0` and sources or invokes `build.bash`, causing build tags and backend selection to exclude OpenSSL-dependent code.

Control flow and state: The script is a thin environment wrapper. Persistent state is the resulting static or pure-Go binary.

Dependencies and integration points: Used by CI, release packaging, and portability checks. It validates that gocryptfs remains buildable without C toolchains or OpenSSL libraries.

Risks and test signals: Risks include accidental cgo dependency or build-script behavior that ignores `CGO_ENABLED`. Signals are successful no-OpenSSL build and tests using Go crypto backends.
