<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Makefile -->
# sources/test-tools/kdevops/workflows/steady_state/Makefile

## Purpose
This Makefile exposes kdevops targets for the SSD steady-state workflow.

## Important Targets and Variables
It adds phony targets `steady-state`, `steady-state-files`, `steady-state-prefill`, `steady-state-run`, and `steady-state-help-menu`. `SSD_STEADY_STATE_DYNAMIC_RUNTIME_VARS` sets `"kdevops_run_ssd_steady_state": True`.

## Control Flow
`steady-state-files` runs `playbooks/steady_state.yml` with tags `vars,setup`. `steady-state-prefill` runs `vars,prefill`. `steady-state-run` runs `vars,steady_state`. `steady-state` passes the runtime variable and runs the broader playbook. Help text is appended to `HELP_TARGETS`.

## State, Persistence, and Dependencies
State flows through Ansible vars, generated template files, prefilled storage devices, fio results, and any copied logs. Dependencies are `extra_vars.yaml`, `LIMIT_HOSTS`, and the steady-state playbook.

## Risks and Test Signals
Because prefill can be destructive, separating files, prefill, and run targets is operationally important. The all-in target hides phase boundaries and should be used only when the configured device is confirmed. Test signals are playbook completion and the produced fio steady-state output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Makefile -->
