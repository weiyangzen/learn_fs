## sources/security-integrity/attr/test/Makemodule.am

Purpose: Automake test integration for attr CLI transcripts.

It lists test scripts/data, forces `LC_MESSAGES=C`, puts build and test helper directories on `PATH`, and uses `test/run` as `TEST_LOG_COMPILER`. State is test execution environment. Dependencies are Automake test harness and Perl runner. Risks are path-order assumptions and locale-only normalization, leaving filesystem xattr support as an external prerequisite. Test signal is `make check`.
