# sources/sync-backup/borg/src/borg/testsuite/platform/freebsd_test.py

Purpose: FreeBSD-only ACL tests for access/default ACL round trips and numeric/name conversion.

Important APIs and control flow: module-level marks skip non-FreeBSD and fakeroot. Helpers wrap `acl_get`/`acl_set` with `acl_access`, `acl_default`, and `acl_nfs4` fields. `test_access_acl` checks setting root/wheel named ACL entries, reading named and numeric versions, and preserving explicit numeric ids when requested. `test_default_acl` writes access and default ACL blobs on a directory and expects exact bytes back. NFSv4 ACL testing is noted as not implemented.

State and persistence: creates temporary files/directories and writes ACL metadata.

Dependencies and integration points: depends on Borg platform ACL functions and shared skip markers. Used for archive ACL preservation on FreeBSD.

Risks: requires ACL support and expected root/wheel mappings. Exact ACL byte ordering/format is platform-specific.

Test signals: expected ACL substrings for named/numeric reads and exact access/default ACL roundtrip.
