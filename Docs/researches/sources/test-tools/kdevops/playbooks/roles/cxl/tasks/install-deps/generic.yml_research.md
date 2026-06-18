<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml

Source read: complete file, 9 lines, 254 bytes, sha256 `12c4933fb4f0d00d`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml_research.md`.

Purpose: install CXL workflow packages common to all supported distributions.

Important APIs/types/functions: `ansible.builtin.package` installs `numactl` under sudo.

Control flow: single package task imported after distro-specific CXL dependencies.

State and persistence behavior: changes package state by ensuring numactl is installed.

Dependencies and integration: useful for memory locality inspection/testing after CXL/DAX memory is onlined.

Risks: package name is assumed common across supported distros.

Test signals: `numactl --hardware` should work after the dependency phase.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/generic.yml -->
