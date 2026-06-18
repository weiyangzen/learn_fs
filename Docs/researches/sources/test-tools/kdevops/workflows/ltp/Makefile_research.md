## sources/test-tools/kdevops/workflows/ltp/Makefile

Purpose: Emits LTP workflow variables and defines targets to setup, run, reset, and display LTP results.

Important APIs/types/functions: Uses `LTP_ARGS`, `LTP_ENABLED_TEST_GROUPS`, `WORKFLOW_ARGS`, `WORKFLOW_ARGS_SEPARATED`, and targets `ltp`, `ltp-baseline`, `ltp-dev-baseline`, `ltp-dev-reset`, `ltp-show-results`, and `ltp-help-menu`.

Control flow: Maps every group symbol to explicit true/false vars and appends enabled group labels. Results path is based on `workflows/ltp/results/last-kernel.txt`; targets invoke `ltp.yml` with setup or run/copy tags.

State and persistence: Reads result metadata and logs. Runtime state is created by Ansible on guests and copied into workflow result directories.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `extra_vars.yaml`, baseline/dev host groups, and result directory conventions.

Risks and test signals: False vars are emitted for disabled groups, which is useful but must match Ansible expectations. Test with a minimal group selection and inspect playbook variable decisions and copied logs.
