<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/test_passwd.c -->
# sources/security-integrity/acl/test/test_passwd.c

Purpose: LD_PRELOAD passwd database shim used by tests for deterministic user-name/user-id lookups and ERANGE retry behavior. The file is 158 lines.

Important APIs and functions: Key symbols include `test_getpwent_r`, `test_getpw_match`, `match_name`, `getpwnam_r`, `match_uid`, `getpwuid_r`, `TEST_PASSWD`, `ALIGN_MASK`, `ALIGN`.

Control flow: Parses `test/test.passwd`, implements `getpwnam_r`, `getpwuid_r`, and wrappers, forces growing-buffer paths for name lookups, and returns fixture-backed passwd records.

State and persistence: Test state is temporary directories, environment variables, fixture passwd/group files, expected-output arrays, generated POTFILES metadata, or process-local NSS replacement buffers. Scripts may overwrite generated test/po artifacts but do not modify production ACL source behavior.

Dependencies and integration points: Integrates Perl, shell, libc NSS function interposition, Automake `TESTS`, `LD_PRELOAD`, fixture files, compiled tools on PATH, gettext maintenance, and the libmisc uid/gid lookup code under test.

Risks: Harness quoting, regex comparison, environment substitution, and preload availability can hide or expose failures differently across hosts. Fixture shims are intentionally non-general and should remain isolated to tests.

Test signals: `make check`, running individual `.test` files through `test/runwrapper`, verifying preload use with `.libs/libtestlookup.so`, exercising ERANGE lookup retries, recursive output sorting, and regenerating `po/POTFILES.in` after source-list changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/test_passwd.c -->
