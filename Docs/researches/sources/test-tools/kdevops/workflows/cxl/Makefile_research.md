# sources/test-tools/kdevops/workflows/cxl/Makefile

## Purpose
Maps CXL Kconfig values into Ansible variables and exposes CXL setup, test, result, memory, and dynamic-capacity targets.

## Important APIs, Types, and Functions
Key variables are `CXL_ARGS`, `CXL_DYNAMIC_RUNTIME_VARS`, `WORKFLOW_ARGS`, and `BOOTLINUX_CXL_HELP`. Targets include `cxl`, `cxl-test-probe`, `cxl-test-meson`, `cxl-results`, `cxl-mem-setup`, `cxl-create-dc-region`, and `cxl-dcd-setup`.

## Control Flow
The Makefile assembles ndctl and optional CXL DCD variables, includes `Makefile.kernel`, then runs `playbooks/cxl.yml` with tags matching each operation.

## State and Persistence Behavior
State persists in target-node ndctl checkouts, CXL memory/device setup, and copied results. The Makefile contributes variables to generated workflow args.

## Dependencies and Integration Points
Integrates with `playbooks/cxl.yml`, `workflows/cxl/Makefile.kernel`, QEMU DCD topology configuration, and host limiting.

## Risks and Edge Cases
`CXL_DYNAMIC_RUNTIME_VARS` embeds a Kconfig `y/n` value where downstream may expect boolean syntax. DCD targets require matching QEMU topology. Help text contains a typo for ndctl.

## Test Signals
Run `make -n` under CXL test enabled/disabled and DCD enabled/disabled. Execute probe/meson on a capable disposable environment.
