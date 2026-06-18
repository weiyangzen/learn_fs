<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml

Source read: complete file, 13 lines, 606 bytes, sha256 `1ebb1168b057ad03`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml_research.md`.

Purpose: OS-family dispatcher for CXL/ndctl dependency installation, plus common package installation.

Important APIs/types/functions: `import_tasks` for Debian, SUSE, RedHat, then `import_tasks: generic.yml`.

Control flow: import the distro-specific dependency file based on `ansible_facts['os_family']|lower`, then always import common dependencies.

State and persistence behavior: no direct mutation except imported package installs and facts.

Dependencies and integration: called at the beginning of the CXL main role before ndctl clone/build and CXL setup.

Risks: unsupported OS families still run generic `numactl` install but skip ndctl build dependencies. Static import path uses `tasks/install-deps/...`, requiring role-relative resolution.

Test signals: distro dry runs should show exactly one distro file plus generic file.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/main.yml -->
