# sources/sync-backup/borg/src/borg/testsuite/platform/platform_test.py

Purpose: shared platform-test helpers and basic process identity/liveness tests.

Important APIs and control flow: helper functions detect fakeroot, check if a username exists, and cache `are_acls_working()` by writing a temporary file and trying representative Darwin/Linux/FreeBSD ACL writes/reads. The module defines skip markers for OS, POSIX, fakeroot, ACL availability, Windows, and a specific non-ASCII user. Tests assert `process_alive` is true for current process identity, still true for host/tid variants that Borg treats as local-compatible, and false for a free PID; `test_process_id` validates tuple types, positive pid, non-empty hostname, and stable identity within a thread.

State and persistence: creates a temporary ACL probe file and uses cached result. Reads environment `FAKEROOTKEY` and local user database.

Dependencies and integration points: depends on platform flags, `acl_get`, `acl_set`, `get_process_id`, `process_alive`, testsuite `unopened_tempfile`, and the `free_pid` fixture from fslocking tests. Shared skip markers control OS-specific platform modules.

Risks: ACL probe behavior depends on filesystem and permissions. `free_pid` is inherently racy. Hostname/tid liveness semantics are Borg-specific and may differ from operating-system process APIs.

Test signals: skip-marker construction, current process liveness, dead PID non-liveness, and stable process id tuple.
