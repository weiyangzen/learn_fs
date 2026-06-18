# sources/test-tools/kdevops/kconfigs/workflows/Kconfig

Purpose: central Kconfig workflow selector for kdevops. It enables provisioning, selects distro/custom/packaged Linux kernel strategy, exposes dedicated or mixed subsystem workflows, and sources each workflow-specific Kconfig.

Important APIs/types/functions: defines `WORKFLOWS`, Linux kernel choice symbols `WORKFLOW_LINUX_DISTRO`, `WORKFLOW_LINUX_CUSTOM`, `WORKFLOW_LINUX_PACKAGED`, `BOOTLINUX`, `WORKFLOWS_TESTS`, `WORKFLOWS_LINUX_TESTS`, `WORKFLOWS_DEDICATED_WORKFLOW`, many `KDEVOPS_WORKFLOW_DEDICATE_*` selectors, `KDEVOPS_WORKFLOW_NAME`, and `KDEVOPS_WORKFLOW_ENABLE_*` output symbols. It sources shared, bootlinux, Linux, demo, fstests, blktests, cxl, pynfs, selftests, gitr, ltp, nfstest, sysbench, mmtests, fio-tests, ai, vllm, minio, build-linux, steady-state, and rcloud fragments.

Control flow: `WORKFLOWS` selects Ansible provisioning. Kernel choice determines whether bootlinux is active. If tests are enabled, a dedicated workflow choice selects one subsystem and sets `KDEVOPS_WORKFLOW_NAME`; mixed mode enables independent booleans for several workflows. Each enable symbol then conditionally sources the workflow's Kconfig subtree.

State/persistence behavior: `.config` selections become generated YAML and make targets. Dedicated workflow selection persists the canonical workflow name such as `fstests`, `blktests`, `ai`, `minio`, or `build-linux`; mixed mode uses `mix`. `KDEVOPS_WORKFLOW_GIT_CLONES_KDEVOPS_GIT` defaults on for fstests/blktests.

Dependencies/integration: this file is the menu root that connects Kconfig to Ansible playbooks and workflow directories. It depends on symbols such as `QEMU_ENABLE_EXTRA_DRIVE_LARGEIO`, `BOOTLINUX_BUILDER`, `KDEVOPS_USE_DECLARED_HOSTS`, `LIBVIRT`, and `TERRAFORM_PRIVATE_NET` from other fragments.

Risks/test signals: duplicated `source "workflows/pynfs/Kconfig"` and an incorrect LTP endif comment are maintenance hazards. Some help text contains typos, and mixed workflow support warns that baseline/dev targets may not behave as dedicated workflows expect. Test signals are successful `menuconfig`, generated YAML with expected workflow name/enables, and all sourced Kconfig paths existing.
