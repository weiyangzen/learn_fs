## sources/test-tools/kdevops/workflows/nfstest/Makefile

Purpose: Emits nfstest Ansible variables and defines setup/run/reset/results targets.

Important APIs/types/functions: Uses `NFSTEST_ARGS`, `NFSTEST_ENABLED_TEST_GROUPS`, `WORKFLOW_ARGS`, `WORKFLOW_ARGS_SEPARATED`, and targets `nfstest`, `nfstest-baseline`, `nfstest-dev-baseline`, `nfstest-dev-reset`, `nfstest-show-results`, and `nfstest-help-menu`.

Control flow: Chooses kdevops or external NFS server args, appends mount path, repo/ref, selected group labels, computes result find path from `last-kernel.txt`, and invokes `nfstest.yml` with setup or run/copy tags.

State and persistence: Reads result metadata/logs; Ansible handles nfstest installation and result copying.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `extra_vars.yaml`, baseline/dev host groups, and result directory layout.

Risks and test signals: External server branch references `CONFIG_NFSTEST_NFS_SERVER_HOSTNAME` and `CONFIG_NFSTEST_NFS_SERVER_EXPORT`, but the Kconfig defines `NFSTEST_NFS_SERVER_HOST` and no export symbol in the listed file. Test external-server mode specifically, as generated vars may be empty.
