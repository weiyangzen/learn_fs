<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/main.yml

Purpose: orchestrates repeated reboot tests, including optional regular-vs-kexec comparison, result directory setup, reset handling, loop execution, and result fetching.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.include_tasks`, `ansible.builtin.file`, `ansible.builtin.set_fact`, `ansible.builtin.fetch`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `become_method`, `reboot_limit_analyze_file`, `reboot_limit_count_file`, `label`, `reboot_limit_local_results_dir`, `with_sequence`, `loop_var`; tasks `Import optional extra_args file`, `Install dependencies for reboot-limit`, `Create the reboot-limit data collection directory for each host`, `Create the regular reboot data collection directory for comparison mode`, `Create the kexec reboot data collection directory for comparison mode`.

Control flow: Loads extra vars, prepares data partition and dependencies, creates result dirs, sets analyze/count file facts, handles reset tags, creates local result dir, loops through `do-reboot.yml` or `do-reboot-compare.yml`, then fetches analyze/count logs.

State and persistence behavior: Persists boot count and systemd-analyze logs on targets plus copied results under `workflows/demos/reboot-limit/results`.

Dependencies and integration points: Depends on reboot-limit defaults, package deps, Ansible reboot connectivity, and optional kexec support.

Risks: Running this role intentionally disrupts hosts. Comparison mode changes paths but `reboot_limit_analyze_file` initially points at single-mode data.

Test signals: Signals are exact number of boot-count increments, fetched logs, successful reconnection after each reboot, and mode-specific result directories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/main.yml -->
