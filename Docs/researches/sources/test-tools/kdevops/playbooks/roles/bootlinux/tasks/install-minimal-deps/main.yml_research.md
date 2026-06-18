# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-minimal-deps/main.yml

This dispatcher imports minimal dependency tasks for Debian, SUSE, or Red Hat based on `ansible_os_family`. It is selected by `bootlinux/tasks/main.yml` when `bootlinux_9p` is true and packaged workflow mode is disabled.

Important APIs are conditional `import_tasks`. State changes occur only in the imported distro files. Integration points are 9P mode, target guest package managers, and the later kernel install steps. Risks include silent no-op on unsupported OS families, exact OS-family spelling, and the possibility that minimal dependencies are insufficient for distro-specific install hooks. Test signals should include fact-matrix include validation and a 9P install smoke test on each supported family.
