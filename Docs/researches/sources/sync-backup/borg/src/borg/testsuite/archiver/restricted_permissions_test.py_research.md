<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/restricted_permissions_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/restricted_permissions_test.py

Purpose: local-only tests for repository permission modes controlled by `BORG_REPO_PERMISSIONS`.

Important APIs: `cmd`, `create_test_files`, `changedir`, `PermissionDenied`, and permission values `all`, `no-delete`, `read-only`, `write-only`.

Control flow: each test creates a repo under full permissions, then switches permission mode and exercises allowed/disallowed commands. `all` permits create/delete/repo-delete. `no-delete` permits create/list/check but rejects archive deletion, rename, repo-delete, compact, and repair. `read-only` permits list/extract but rejects create/delete/repo-delete/compact. `write-only` permits new archive creation, rejects reads/deletes/compact/check/repo-delete, then switches to read-only to verify both archives are readable.

State and persistence: environment variable changes gate repository backend operations. Archives and repository state persist across mode switches.

Dependencies/integration: depends on borgstore permission enforcement and local archiver behavior; only generated for local kinds. Risks include permission matrix drift and commands that internally read before writing. Test signals are successful allowed commands and `PermissionDenied` exceptions for blocked operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/restricted_permissions_test.py -->
