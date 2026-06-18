<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/rxe/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/rxe/tasks/main.yml

Purpose: configures software RoCE (`rdma_rxe`) support by installing a udev rule and reloading udev so target devices are created.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.template`, `ansible.builtin.shell`; variables/facts `file`, `with_first_found`, `skip`, `failed_when`, `become_method`, `force`, `changed_when`; tasks `Include optional extra_vars`, `Insert a udev rule to create an rxe device`, `Reload the udev ruleset`.

Control flow: Loads optional extra vars, templates `99-rxe.rules` or equivalent udev rule, and triggers udev reload.

State and persistence behavior: Persists a udev rules file and affects device creation state.

Dependencies and integration points: Used by workflows needing RXE RDMA devices.

Risks: Incorrect udev rule paths differ by distro; reload without module/device validation may hide failures.

Test signals: Signals are installed rule, udev reload success, loaded rdma_rxe support, and visible RDMA device.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/rxe/tasks/main.yml -->
