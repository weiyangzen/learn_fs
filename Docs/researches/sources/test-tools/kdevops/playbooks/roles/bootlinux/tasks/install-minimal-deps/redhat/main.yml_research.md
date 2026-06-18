# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/redhat/main.yml

This Red Hat minimal dependency file installs `make`, `gcc`, `kmod`, and `ccache` with DNF for 9P mode. It has two nearly identical tasks split by distribution major version less than 8 versus greater than or equal to 8; both currently use `ansible.builtin.dnf`.

Important APIs are privileged `dnf` and `ansible_facts['distribution_major_version']`. Persistent state is installed minimal packages. Integration points are bootlinux 9P mode and kernel installation hooks on Red Hat family guests. Risks include redundant version split, use of DNF even for older releases where yum compatibility may vary, and no retry logic. Test signals should include RHEL/CentOS 7 and 8+ package installation and a follow-on `make modules_install install` check.
