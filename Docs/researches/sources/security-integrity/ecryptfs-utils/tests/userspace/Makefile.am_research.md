## sources/security-integrity/ecryptfs-utils/tests/userspace/Makefile.am

Purpose: Automake fragment for userspace libecryptfs tests. It marks `verify-passphrase-sig.sh` as a distributed `make check` script and builds helper binaries for passphrase signature and wrap/unwrap tests.

Important APIs and functions: `AUTOMAKE_OPTIONS = subdir-objects`, `dist_check_SCRIPTS`, `check_PROGRAMS`, `dist_noinst_DATA`, `dist_noinst_SCRIPTS`, conditional `if ENABLE_TESTS`, `_SOURCES`, `_LDADD`, and `TESTS`. Control flow is declarative: under tests-enabled builds, compile `verify-passphrase-sig/test` and `wrap-unwrap/test`, both linked against libecryptfs.

State and persistence: Build artifacts only. Dependencies are automake, libtool, and libecryptfs. Integration: `make check` runs only `verify-passphrase-sig.sh`; `wrap-unwrap.sh` is distributed but not in `TESTS`, likely run manually or by the custom harness. Risks are coverage gaps if non-`TESTS` scripts are assumed to run in CI.
