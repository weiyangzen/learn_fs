<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/visualize.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/visualize.yml

Purpose: localhost visualization aggregator for monitoring result directories.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.command`, `ansible.builtin.debug`, `ansible.builtin.find`; variables/facts `cmd`, `failed_when`, `changed_when`, `msg`, `patterns`, `recurse`; tasks `Check if monitoring data was collected`, `Generate monitoring visualizations`, `Generate folio migration comparison plots`, `Display folio migration visualization results`, `Generate fragmentation comparison plots`.

Control flow: Stats the result directory, then runs folio migration, simple fragmentation, and A/B fragmentation comparison scripts. It lists generated PNG/HTML files from the root and `fragmentation` subdirectory.

State and persistence behavior: Writes only generated visualization artifacts in the monitoring results tree.

Dependencies and integration points: Included by `monitor_collect.yml`; depends on Python plotting dependencies on localhost and scripts under `role_path`.

Risks: Commands are `failed_when: false`, so visualization failures may be visible only in debug output. The legacy fragmentation script may produce low-value graphs.

Test signals: Signals include non-empty stdout from scripts, generated PNG files, and harmless behavior when no data exists.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/visualize.yml -->
