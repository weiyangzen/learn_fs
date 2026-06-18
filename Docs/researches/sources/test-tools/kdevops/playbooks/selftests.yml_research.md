# sources/test-tools/kdevops/playbooks/selftests.yml

Purpose: wrapper playbook to configure and run Linux kernel selftests.

Important APIs/types/functions: targets `baseline:dev` and invokes role `selftests`.

Control flow: hands execution to the role after host selection.

State/persistence behavior: delegated to `selftests` role.

Dependencies/integration: integrates with baseline/dev kdevops workflow.

Risks/test signals: wrapper-level risk is role or inventory drift. Test signals are role execution and selftest result artifacts.
