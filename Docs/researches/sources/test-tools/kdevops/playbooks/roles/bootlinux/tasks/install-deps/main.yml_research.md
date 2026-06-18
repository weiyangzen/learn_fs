# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/install-deps/main.yml

This dispatcher imports full kernel build dependency tasks for Debian, SUSE, or Red Hat based on `ansible_os_family`. It is used when bootlinux builds happen on target nodes rather than 9P host builds and when packaged workflow mode is disabled.

Important APIs are conditional `import_tasks`. Control flow is static and OS-family driven. Persistent state is delegated to the distro files, which install package sets. Integration points are `bootlinux/tasks/main.yml`, distro fact gathering, and the target build mode. Risks include unsupported OS families silently doing nothing, exact family spelling requirements (`Suse`, `RedHat`), and syntax errors in any imported file affecting playbook parsing. Test signals should include syntax checks and fact-driven include tests for all three supported families.
