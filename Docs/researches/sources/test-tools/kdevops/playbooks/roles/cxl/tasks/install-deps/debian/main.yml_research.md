<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml

Source read: complete file, 33 lines, 646 bytes, sha256 `ef8181cb5280dcf1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml_research.md`.

Purpose: Debian-family dependency setup for building ndctl/cxl tooling.

Important APIs/types/functions: `ansible.builtin.apt` updates cache and installs git, meson, gcc, pkg-config, cmake, kmod/udev/uuid/json-c/keyutils/iniparser/traceevent/tracefs development headers, asciidoctor, bash-completion, and jq.

Control flow: update apt cache, then install the package list.

State and persistence behavior: changes apt package state on the target.

Dependencies and integration: supports `meson setup build`, ndctl/cxl compilation, documentation, shell completion, JSON handling, and trace libraries in the CXL main role.

Risks: package names target modern Debian/Ubuntu; older releases may lack tracefs/traceevent dev packages. No retry is configured.

Test signals: after installation, `meson setup build` in ndctl should find kmod, udev, uuid, json-c, keyutils, iniparser, traceevent, and tracefs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/debian/main.yml -->
