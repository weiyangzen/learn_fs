<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/tasks/main.yml

Purpose: installs, configures, runs, and collects results for the external nfstest suite in a kdevops workflow.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.package`, `ansible.builtin.include_role`, `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.git`, `ansible.builtin.template`, `ansible.builtin.command`; variables/facts `file`, `with_first_found`, `skip`, `failed_when`, `params`, `become_flags`, `become_method`, `nfstest_install_dir`, `nfstest_test_group`, `nfstest_nfs_server_export`; tasks `Include optional extra_vars`, `Set OS-specific variables`, `Install dependencies for nfstest`, `Create the /data mount point on the target nodes`, `Set the pathname of the install directory`.

Control flow: Loads optional/OS vars, installs dependencies, prepares `/data`, removes old install dir, derives host test group, optionally creates an NFS export, clones nfstest, templates and runs `/tmp/runtest.sh`, records kernel version, fetches `nfstest*.log`, and archives last-run results.

State and persistence behavior: Persists cloned source under data path, target mount point, optional server export, temporary run script/logs, and localhost results under `workflows/nfstest/results`.

Dependencies and integration points: Depends on distro package vars, git, templates per test group, NFS server/export roles, and dedicated workflow variables.

Risks: The so-called full clone also uses `depth: 1`. Test-group derivation is host-name-convention-dependent. Cleaning last-run is delegated run-once and can erase concurrent results.

Test signals: Signals are dependency install, successful clone, mounted export, logs fetched per kernel, and no TAP/log failures in generated nfstest output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/tasks/main.yml -->
