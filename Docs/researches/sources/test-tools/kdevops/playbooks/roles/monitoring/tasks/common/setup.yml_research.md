<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/common/setup.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/common/setup.yml

Purpose: shared setup for monitoring collection. It resolves a workflow-specific local monitoring results path and creates the delegated localhost directory when monitoring is enabled.

Important APIs/types/functions: modules `ansible.builtin.debug`, `ansible.builtin.set_fact`, `ansible.builtin.file`; variables/facts `msg`, `monitor_developmental_stats`, `monitor_folio_migration`, `enable_monitoring`, `kdevops_run_fstests`, `kdevops_run_blktests`, `kdevops_workflow_enable_sysbench`, `monitoring_results_path`; tasks `Debug monitoring collection start`, `Set workflow-appropriate monitoring results path`, `Create local monitoring results directory`.

Control flow: Runs a debug task showing monitor flags, sets `monitoring_results_path` to `{{ topdir_path }}/workflows/{{ kdevops_workflow_name }}/results/monitoring`, then creates the directory once on localhost.

State and persistence behavior: Persists only the localhost results directory. The path fact is consumed by later fetch and visualization tasks.

Dependencies and integration points: Imported by monitor collection entrypoints before folio or fragmentation collectors. Depends on `topdir_path`, `kdevops_workflow_name`, and monitor enable flags.

Risks: The directory creation is skipped unless enable flags align; later tasks also reset the path in places, so inconsistent path logic can split outputs.

Test signals: Ansible parseability, debug output with expected booleans, and created localhost directory are the main test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/common/setup.yml -->
