<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml

Source read: complete file, 10 lines, 511 bytes, sha256 `16590314d9da8032`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml_research.md`.

Purpose: OS-family dispatcher for partition creation dependencies.

Important APIs/types/functions: `import_tasks` for Debian, SUSE, and RedHat dependency files selected by `ansible_facts['os_family']|lower`.

Control flow: exactly one distro-specific package file should run on supported systems.

State and persistence behavior: no direct mutation; imported files install filesystem tools and may set SUSE facts.

Dependencies and integration: called before destructive or mounting operations in `create_partition/tasks/main.yml`.

Risks: unsupported OS families proceed without installing mkfs tools. Static import paths include `tasks/install-deps/...`, depending on role-relative resolution.

Test signals: syntax check plus per-distro dry runs should verify import path resolution and package-manager selection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/main.yml -->
