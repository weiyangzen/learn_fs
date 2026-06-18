<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/main.yml

Purpose: top-level monitoring role task switchboard for run and collect phases.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.include_tasks`; variables/facts `ignore_errors`, `with_first_found`, `skip`; tasks `Import optional extra_args file`, `Include monitor_run tasks`, `Include monitor_collect tasks`.

Control flow: Imports optional extra vars, includes `monitor_run.yml` when `monitor_run` is true, and includes `monitor_collect.yml` when `monitor_collect` is true.

State and persistence behavior: No direct persistent state beyond loaded variables; included task files create monitor outputs.

Dependencies and integration points: Entry point for playbooks that invoke the monitoring role.

Risks: If both booleans are false this role is a no-op. Extra-vars load ignores errors, which can hide malformed overrides.

Test signals: Signals are correct tag selection and inclusion of run or collect tasks under requested booleans.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/main.yml -->
