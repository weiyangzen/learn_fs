# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/suse/main.yml

This SUSE minimal dependency file installs the small tool set needed by 9P kernel installation mode: `make`, `gcc`, `kmod-compat`, and `ccache`.

The important API is privileged `community.general.zypper`. Persistent state is the installed package set. Integration points are bootlinux 9P mode and SUSE kernel module/install tooling. Risks include `kmod-compat` availability varying by SUSE release, no retry logic, and assuming ccache is useful even when the guest is only installing artifacts. Test signals should include package resolution on supported SLE/openSUSE releases and a kernel install smoke test after the 9P mount is present.
