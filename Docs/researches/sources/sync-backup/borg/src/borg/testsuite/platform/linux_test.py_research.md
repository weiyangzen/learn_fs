# sources/sync-backup/borg/src/borg/testsuite/platform/linux_test.py

Purpose: Linux-only ACL tests for POSIX ACL round trips, non-ASCII names, and numeric/name conversion helpers.

Important APIs and control flow: module-level marks skip non-Linux and fakeroot. Helpers wrap `acl_get`/`acl_set`. Access/default ACL tests set root and numeric entries, then compare named and numeric forms. `test_non_ascii_acl` is additionally skipped unless a user named `ubel` with umlaut exists; it checks non-ASCII user/group ACL roundtrips and numeric conversion. Utility tests import Linux-specific functions for local uid/gid fallback and numeric-to-named/numeric-with-id transformations, monkeypatching platform user/group lookup to simulate existing and missing ids.

State and persistence: creates temp files/directories and writes ACLs. Monkeypatches platform uid/gid lookup functions.

Dependencies and integration points: depends on `borg.platform.acl_get`, `acl_set`, Linux ACL helper internals, shared skip markers, and platform user/group lookup. It supports ACL archive metadata portability.

Risks: ACL availability, fakeroot, and local user database strongly affect coverage. Non-ASCII ACL test requires a special local user and is commonly skipped.

Test signals: expected ACL byte substrings, exact access/default ACL bytes, fallback uid/gid conversion, and transformed ACL lines with appended ids.
