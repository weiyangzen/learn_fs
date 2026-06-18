<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Suse.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Suse.yml

Purpose: defines the package set required to run nfstest on Suse family systems.

Important APIs/types/functions: variables/facts `nfstest_packages`.

Control flow: Loaded by `nfstest/tasks/main.yml` through `first_found` and passed to `ansible.builtin.package`.

State and persistence behavior: No persistent state beyond package names.

Dependencies and integration points: Supports nfstest dependency installation across distros.

Risks: Missing Python, git, or NFS client packages will cause later clone/mount/test failures.

Test signals: Signal is successful package installation and ability to run the generated nfstest script.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Suse.yml -->
