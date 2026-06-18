<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/handle-reboot-data.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/handle-reboot-data.yml

Purpose: post-processes or displays collected reboot-limit data after loop execution.

Important APIs/types/functions: modules `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.stat`, `ansible.builtin.slurp`, `ansible.builtin.copy`, `ansible.builtin.command`, `ansible.builtin.lineinfile`; variables/facts `reboot_type_analyze_file`, `reboot_type_count_file`, `become_method`, `reboot_type_count`, `content`, `line`, `create`; tasks `Set reboot type specific file paths`, `Create the data collection directory for {{ reboot_type }} reboot type`, `Check if the {{ reboot_type }} reboot count file exists`, `Read last {{ reboot_type }} boot count`, `Set the current {{ reboot_type }} boot count into a variable`.

Control flow: Reads target or local logs, organizes data for reporting, and emits debug/summary output according to workflow tags.

State and persistence behavior: May create or update local result summaries but does not perform reboots.

Dependencies and integration points: Integrated with reboot-limit result handling tasks or workflow reporting.

Risks: Parsing depends on `systemd-analyze` output format and expected count log names.

Test signals: Signals are readable summaries and graceful behavior with missing optional logs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/handle-reboot-data.yml -->
