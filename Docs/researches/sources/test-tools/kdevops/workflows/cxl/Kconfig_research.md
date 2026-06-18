# sources/test-tools/kdevops/workflows/cxl/Kconfig

## Purpose
Configures the CXL workflow: whether to run mock CXL device tests and where to clone/build ndctl.

## Important APIs, Types, and Functions
Important symbols are `ENABLE_CXL_TEST`, `NDCTL_GIT`, `NDCTL_DATA`, and `NDCTL_VERSION`.

## Control Flow
All options are gated by `KDEVOPS_WORKFLOW_ENABLE_CXL`. Git URL defaults switch between upstream pmem/ndctl and linux-kdevops GitHub/GitLab alternatives based on global git settings.

## State and Persistence Behavior
Kconfig choices persist in `.config` and generated YAML. `NDCTL_DATA` controls target-node clone location.

## Dependencies and Integration Points
Consumed by `workflows/cxl/Makefile`, CXL Ansible roles, ndctl/cxl tooling, and optional QEMU CXL topology configuration elsewhere.

## Risks and Edge Cases
`NDCTL_VERSION` defaults to `v74`, while help text says only a pending branch builds correctly. CXL testing also depends on kernel/QEMU capabilities outside this file.

## Test Signals
Validate upstream/GitHub/GitLab git modes, ndctl build at configured version, and probe/meson targets with tests enabled/disabled.
