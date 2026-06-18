<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/main.yml

Purpose: configures an NFS server host for kdevops workflows, including package dependencies, `/etc/nfs.conf`, optional iSCSI/local storage prep, SELinux policy, firewall handling, and nfs-server service state.

Important APIs/types/functions: modules `ansible.builtin.include_tasks`, `ansible.builtin.template`, `ansible.builtin.include_role`, `ansible.builtin.file`, `ansible.builtin.command`, `ansible.builtin.copy`, `community.general.sefcontext`, `ansible.builtin.service_facts`; variables/facts `become_flags`, `become_method`, `tasks_from`, `volume_group_name`, `changed_when`, `failed_when`, `target`, `setype`, `enabled`; tasks `Debian-specific setup`, `SuSE-specific setup`, `Red Hat-specific setup`, `Generate /etc/nfs.conf`, `Set up an iSCSI initiator`.

Control flow: Dispatches distro dependency tasks, templates `nfs.conf`, optionally includes `iscsi` or `volume_group`, creates the export root, installs a custom SELinux policy when enabled, labels exports as `public_content_rw_t`, stops firewalld, and reloads/enables `nfs-server.service`.

State and persistence behavior: Mutates packages, `/etc/nfs.conf`, export directories, SELinux module/state, firewalld state, and systemd service state.

Dependencies and integration points: Foundation for `nfsd_add_export`, `pynfs`, and `nfstest`. Depends on templates, SELinux tooling, nfs-utils packages, and optional storage roles.

Risks: Disabling firewalld is broad. SELinux setup assumes policy tooling exists. Service reload before exports exist can hide template issues until clients mount.

Test signals: Signals are idempotent package install, rendered config, active nfs-server, correct SELinux labels, and successful `exportfs -v` after adding exports.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/main.yml -->
