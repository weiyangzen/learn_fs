# sources/test-tools/kdevops/workflows/Makefile

Purpose: central workflow Makefile that conditionally includes individual kdevops workflow Makefiles and accumulates Ansible extra variables.

Important variables are `WORKFLOW_ARGS`, `WORKFLOW_ARGS_SEPARATED`, `BOOTLINUX_ARGS`, `ANSIBLE_EXTRA_ARGS`, `ANSIBLE_EXTRA_ARGS_SEPARATED`, and `ANSIBLE_EXTRA_ARGS_DIRECT`. It includes `workflows/common/Makefile` unconditionally, then includes workflow-specific Makefiles when their `CONFIG_KDEVOPS_WORKFLOW_ENABLE_*` or related config symbols are `y`.

Control flow is GNU Make `ifeq` based on generated config. Bootlinux additionally writes `kdevops_bootlinux='True'` or `'False'`. The one unconditional target is `nfstests-results-visualize`, which runs the nfstest visualization script independent of enabling the full workflow.

State is Make variable accumulation and included target definitions. Integration points are Kconfig-generated `.config`, Ansible playbooks, and each workflow subdirectory. Risks include missing included files when config enables a workflow, ordering effects in `WORKFLOW_ARGS`, and `WORKFLOW_ARGS_DIRECT` being appended without initialization in this file. Test signals should run `make -n` with representative configs and verify expected targets/extra vars are present.
