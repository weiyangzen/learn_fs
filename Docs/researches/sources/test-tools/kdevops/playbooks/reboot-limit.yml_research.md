# sources/test-tools/kdevops/playbooks/reboot-limit.yml

Purpose: Thin playbook entry point for the reboot-limit workflow.

Key APIs and flow: Defines one play, `Configure and run the reboot-limit workflow`, targeting the `baseline:dev` inventory groups and applying the `reboot-limit` role. There are no inline variables or tasks.

State, dependencies, integration: All behavior is delegated to the `reboot-limit` role. This file integrates the role into the standard kdevops baseline/development host split and serves as the playbook invoked by workflow commands.

Risks and test signals: Host pattern requires inventory groups named `baseline` or `dev`; no guard exists for missing role variables because they are role-owned; debugging requires following the role. Tests should validate Ansible syntax, inventory matching, and role variable defaults.
