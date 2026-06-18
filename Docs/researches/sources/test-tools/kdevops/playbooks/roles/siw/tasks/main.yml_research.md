<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/siw/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/siw/tasks/main.yml

Purpose: configures Soft-iWARP (`siw`) device creation through udev.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.template`, `ansible.builtin.shell`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `become_method`, `force`; tasks `Import optional extra_args file`, `Insert udev rule to create siw device on the target host`, `Force the target host to reload its udev ruleset`.

Control flow: Loads optional extra vars, templates `/usr/lib/udev/rules.d/99-siw.rules`, then runs `udevadm control --reload && udevadm trigger`.

State and persistence behavior: Persists a udev rules file and triggers device-rule application.

Dependencies and integration points: Used by RDMA/NFS or storage workflows needing SIW.

Risks: Hard-coded udev rules directory may not match every distro; no explicit validation of resulting siw device.

Test signals: Signals are installed rule, successful udev reload, and expected RDMA device creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/siw/tasks/main.yml -->
