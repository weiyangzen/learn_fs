<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/test_group.c -->
# sources/security-integrity/acl/test/test_group.c

Purpose: LD_PRELOAD group database shim used by tests for deterministic group-name/group-id lookups and ERANGE retry behavior. The file is 165 lines.

Important APIs and functions: Key symbols include `test_getgrent_r`, `test_getgr_match`, `match_name`, `getgrnam_r`, `match_gid`, `getgrgid_r`, `TEST_GROUP`, `ALIGN_MASK`, `ALIGN`.

Control flow: Parses `test/test.group`, implements `getgrnam_r`, `getgrgid_r`, and non-reentrant wrappers, deliberately forces large-buffer retries for name lookups, and returns fixture-backed records.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/test_group.c -->
