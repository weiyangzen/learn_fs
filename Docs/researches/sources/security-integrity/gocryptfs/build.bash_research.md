# sources/security-integrity/gocryptfs/build.bash

Purpose: This is the main gocryptfs build script for producing `gocryptfs` and related binaries with version metadata.

Important APIs and steps: It determines git version information, configures Go build flags/ldflags, compiles the main binary and `gocryptfs-xray`, and may report binary backend information.

Control flow and state: It exits on build errors and writes binaries into the source tree. Version strings are derived from git or fallback files.

Dependencies and integration points: Used by Makefile, CI, release packaging, benchmarks, and no-OpenSSL wrapper.

Risks and test signals: Risks include dirty-tree version ambiguity, missing Go environment, or OpenSSL/cgo incompatibility. Signals are successful binary builds and version output matching expected git/version metadata.
