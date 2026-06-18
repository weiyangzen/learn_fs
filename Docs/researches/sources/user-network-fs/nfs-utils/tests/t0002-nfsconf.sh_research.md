# sources/user-network-fs/nfs-utils/tests/t0002-nfsconf.sh

Purpose: This shell test is intended to validate nfs.conf parser behavior against the nfsconf fixtures.

Important APIs and control flow: It sources the shared test library, points parser commands at fixture files under `tests/nfsconf`, and checks behavior for valid and invalid configuration files. The fixture pairing suggests assertions around parser dump/get/isset semantics and error handling.

State, dependencies, and integration: It depends on the built nfsconf tooling and `srcdir` fixture discovery. It does not manage daemon state.

Risks and test signals: The top-level `Makefile.am` does not list this script in `TESTS` in the inspected snapshot, so it may not run by default. Validation should add it to the test suite if intended, then assert valid include/expansion behavior and deliberate error diagnostics.
