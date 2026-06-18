# sources/test-tools/kdevops/playbooks/roles/bootlinux/tasks/update-grub/main.yml

This dispatcher imports the distro-specific GRUB update task for Debian, SUSE, or Red Hat based on `ansible_facts['os_family']|lower`.

Important APIs are conditional `import_tasks`. Persistent state changes happen in the imported files, which regenerate bootloader configuration. Integration points are bootlinux main uninstall/install flows and `update-grub/install.yml`. Risks include unsupported OS families doing nothing, static import syntax exposure, and relying on lower-case family strings. Test signals should include fact-matrix include checks and verifying each supported distro produces a changed GRUB update after kernel installation.
