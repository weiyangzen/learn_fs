# sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/main.yml

This dispatcher includes the shared `pkg` role and imports the distribution-specific dependency file for Debian, SUSE, or Red Hat based on `ansible_facts['os_family']|lower`.

Important APIs are `include_role` and `import_tasks`. Control flow is purely conditional on gathered OS family facts. State persistence is delegated to the distro files, which install packages and sometimes build NBD. Integration points are role `pkg` and the three distro-specific task files. Risks include no fallback or failure message for unsupported OS families, exact lower-case comparisons that must match Ansible fact values, and static imports making syntax errors in all distro files visible even when not executed. Test signals should include ansible-lint/syntax checks and fact-matrix tests for supported families.
