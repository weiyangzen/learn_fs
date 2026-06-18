<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/run -->
# sources/security-integrity/acl/test/run

Purpose: Perl test harness for ACL scenario files used by `make check`. The file is 375 lines.

Important APIs and functions: Key symbols include `exec_test`, `process_test`, `su`, `sg`.

Control flow: Creates an isolated temp directory, sets TESTDIR/PATH/TUSER/TGROUP, parses `$` command lines with `<` stdin and `>` expected output records, executes commands, compares exact or regex-prefixed output, reports colored status, supports line limits/verbose mode, and cleans up.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/run -->
