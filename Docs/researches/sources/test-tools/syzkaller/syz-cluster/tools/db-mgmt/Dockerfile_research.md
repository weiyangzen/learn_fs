## sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/Dockerfile

This Dockerfile packages the `db-mgmt` utility. It copies `/build/syz-cluster/bin/db-mgmt` from the common builder image into Alpine and sets it as entrypoint.

Integration is with the migration job and local run helper. Risks are minimal but include Alpine runtime compatibility and root execution by default.
