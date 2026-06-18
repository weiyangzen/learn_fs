# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/debian/main.yml

This Debian minimal dependency file supports 9P bootlinux mode, where the kernel build happens on the host and the guest only needs enough tooling for installation. It runs `apt-get update --allow-releaseinfo-change` best-effort, refreshes apt metadata through the apt module, and installs `make`, `gcc`, `kmod`, and `ccache`.

Important APIs are privileged `command` and `apt`. Persistent state is the installed minimal package set. Integration points are 9P build/install tasks and ccache environment variables. Risks include ignoring update-releaseinfo errors, still installing `gcc` even if only module installation is needed, and no retry around apt. Test signals should include a 9P-mode guest provisioning run and verification that `modules_install install` prerequisites exist.
