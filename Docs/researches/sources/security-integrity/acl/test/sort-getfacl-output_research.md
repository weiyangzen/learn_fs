<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/sort-getfacl-output -->
# sources/security-integrity/acl/test/sort-getfacl-output

Purpose: Perl filter that sorts blank-line-separated `getfacl` output records for stable recursive-output comparisons. The file is 4 lines.

Important APIs and functions: Key symbols include No exported code symbols; the file is declarative or script-oriented..

Control flow: Reads all stdin at once, splits records on double newlines, sorts them, and prints records separated by blank lines.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/sort-getfacl-output -->
