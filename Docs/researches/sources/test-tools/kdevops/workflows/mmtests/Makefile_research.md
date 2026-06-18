## sources/test-tools/kdevops/workflows/mmtests/Makefile

Purpose: Defines mmtests setup, run, results, compare, monitor, clean, and help targets.

Important APIs/types/functions: Targets are `mmtests`, `mmtests-baseline`, `mmtests-dev`, `mmtests-tests`, `mmtests-results`, `mmtests-compare`, `monitor-results`, `mmtests-clean`, and `mmtests-help`; shared variable is `MMTESTS_ARGS`.

Control flow: Each target invokes an Ansible playbook with relevant tags and host limits. Baseline/dev targets limit to `mmtests:&baseline` or `mmtests:&dev`; compare uses `mmtests-compare.yml`.

State and persistence: Runtime state is in guest mmtests installations and copied result directories. Make itself does not write state.

Dependencies and integration points: Depends on `playbooks/mmtests.yml`, `playbooks/mmtests-compare.yml`, `playbooks/monitor-results.yml`, `extra_vars.yaml`, and inventory groups.

Risks and test signals: The `mmtests` target has a command line where `$(MMTESTS_ARGS)` appears after a non-continued line, which may be interpreted as a separate shell command. Test `make -n mmtests` to verify emitted commands.
