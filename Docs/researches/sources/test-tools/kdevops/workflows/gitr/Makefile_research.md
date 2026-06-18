## sources/test-tools/kdevops/workflows/gitr/Makefile

Purpose: Converts gitr Kconfig into Ansible vars and defines Make targets to setup, run, reset, and display Git regression test results.

Important APIs/types/functions: Emits `GITR_ARGS` into `WORKFLOW_ARGS_DIRECT`, maintains `GITR_ENABLED_TEST_GROUPS`, and defines targets `gitr`, `gitr-baseline`, `gitr-dev-baseline`, `gitr-dev-reset`, `gitr-show-results`, and `gitr-help-menu`.

Control flow: Includes one filesystem-specific Makefile, adds repo/ref and thread/test arguments, chooses play tags based on all-vs-specific tests, computes result path from `last-kernel.txt`, and invokes `ansible-playbook` against baseline/dev host groups.

State and persistence: Reads `workflows/gitr/results/last-kernel.txt` and result summaries. Writes are performed by the Ansible playbook, not Make directly.

Dependencies and integration points: Depends on `KDEVOPS_PLAYBOOKS_DIR`, `extra_vars.yaml`, inventory groups, filesystem sub-Makefiles, and result layout.

Risks and test signals: `WORKFLOW_ARGS_DIRECT` vs separated args affect how values with spaces are passed. Test by inspecting generated Ansible command lines and running `gitr-show-results` after a known test run.
