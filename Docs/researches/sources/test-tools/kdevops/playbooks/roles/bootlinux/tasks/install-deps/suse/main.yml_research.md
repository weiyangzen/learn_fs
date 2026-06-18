# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/suse/main.yml

This SUSE dependency file installs Linux kernel build dependencies using `community.general.zypper`. The package list includes compilers, git, make, kconfig/build tools, OpenSSL and ELF development libraries, filesystem utilities, mdadm, rpc/portmap, hwinfo, iSCSI, and ccache.

Important APIs are privileged `community.general.zypper` with `disable_recommends: false`. Persistent state is the zypper package database. Integration points are bootlinux build tasks, ccache setup, and SUSE package repositories. Risks include package naming differences between openSUSE and SLE, missing retry logic, and no optional Clang path unlike Red Hat. Test signals should include package resolution on intended SUSE releases and verifying the kernel build can reach configuration and compile phases.
