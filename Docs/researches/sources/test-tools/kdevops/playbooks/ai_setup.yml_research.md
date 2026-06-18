# sources/test-tools/kdevops/playbooks/ai_setup.yml

Purpose: prepares AI benchmark environment on baseline/dev hosts.

Important APIs/types/functions: targets `baseline:dev` and runs role `ai_setup`.

Control flow: all setup sequencing is delegated to the role, usually before install or test playbooks.

State/persistence behavior: creates prerequisite packages, directories, configuration, or service state required for later AI benchmark execution.

Dependencies/integration: depends on role defaults and inventory variables generated from AI workflow Kconfig.

Risks/test signals: because setup is abstracted behind a role, this file mainly tests playbook wiring. Test signals are successful role completion and subsequent install/benchmark playbooks not failing on missing prerequisites.
