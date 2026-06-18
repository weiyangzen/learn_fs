<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/defaults/main.yml

Purpose: sets nfstest repository, commit, mount point, and whether to use kdevops-managed NFS exports.

Important APIs/types/functions: variables/facts `kdevops_run_nfstest`, `kdevops_workflows_dedicated_workflow`.

Control flow: Defaults are consumed by `nfstest/tasks/main.yml` during clone, export setup, and test execution.

State and persistence behavior: No direct state; controls install paths and export behavior.

Dependencies and integration points: Integrated with nfsd/nfsd_add_export and workflow templates.

Risks: Changing repo/commit or server flags alters reproducibility.

Test signals: Signals are expected clone source/version and generated test script using the configured mount.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/defaults/main.yml -->
