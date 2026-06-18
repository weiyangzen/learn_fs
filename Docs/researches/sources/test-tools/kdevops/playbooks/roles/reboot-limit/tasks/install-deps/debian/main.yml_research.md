<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/debian/main.yml

Purpose: installs reboot-limit dependencies for debian, especially tools needed for reboot timing and optional kexec mode.

Important APIs/types/functions: modules `ansible.builtin.apt`; variables/facts `become_method`, `update_cache`; tasks `Install kexec-tools and dependencies for reboot-limit on Debian`.

Control flow: Uses the distro package manager to install the role package list.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by reboot-limit dependency dispatcher.

Risks: Missing `kexec-tools` or systemd utilities cause mode-specific failures later.

Test signals: Signal is package install success and availability of `kexec` when kexec mode is selected.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/debian/main.yml -->
