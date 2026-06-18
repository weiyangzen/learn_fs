<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/main.yml

Purpose: builds and runs pynfs NFSv4 conformance tests against kdevops-created exports, then collects JSON result files by kernel version.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.include_tasks`, `ansible.builtin.git`, `ansible.builtin.command`, `ansible.builtin.include_role`, `ansible.builtin.script`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `pynfs_workflow_dir`, `pynfs_results_full_path`, `pynfs_results_target`, `become_flags`, `become_method`, `repo`, `update`; tasks `Import optional extra_args file`, `Set the path where we collect our local pynfs results`, `Clean up our localhost results directory and files`, `Create the local results directory`, `Install dependencies`.

Control flow: Loads extra vars, prepares local result dirs and data partition, installs dependencies, reclones pynfs, builds it, creates v4.0/v4.1 and optional pNFS exports, waits for NFS grace period, runs workflow scripts, fetches result JSONs, records kernel revision, and archives last-run results.

State and persistence behavior: Persists source under `pynfs_data`, NFS exports on the server, target run outputs, and localhost results under `workflows/pynfs/results`.

Dependencies and integration points: Depends on git, Python build deps, nfsd server host naming, nfsd_add_export, and workflow scripts.

Risks: Server host is derived from prefix as `<prefix>-nfsd`; if inventory differs, export setup fails. Result fetch assumes JSON files are always produced.

Test signals: Signals include build success, grace-period check, result JSONs for v4.0/v4.1 and optional block, and archived last-run directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/main.yml -->
