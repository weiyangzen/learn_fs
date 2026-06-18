# sources/test-tools/kdevops/playbooks/sysbench.yml

Purpose: wrapper playbook for sysbench database benchmark workflow.

Important APIs/types/functions: targets `baseline:dev` and invokes role `sysbench`.

Control flow: selects benchmark hosts and delegates setup/run/collection to sysbench role.

State/persistence behavior: delegated to sysbench role, including package installs, filesystem formatting, database state, telemetry, and results.

Dependencies/integration: depends on baseline/dev groups and role variables.

Risks/test signals: wrapper risk is host group drift. Test signals are sysbench role result artifacts.
