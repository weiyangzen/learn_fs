<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml

Source read: complete file, 27 lines, 583 bytes, sha256 `3bf582a141b6ab73`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family build dependency installation for ndctl/cxl.

Important APIs/types/functions: `ansible.builtin.dnf` installs git-core, meson, cmake, gcc, pkgconf, kmod/systemd/uuid/json-c/keyutils/iniparser/traceevent/tracefs development packages, asciidoctor, bash-completion, and jq.

Control flow: one dnf task with cache update ensures the package list is present.

State and persistence behavior: changes rpm package state.

Dependencies and integration: prepares for ndctl Meson build in `cxl/tasks/main.yml`.

Risks: package availability may require CRB/CodeReady/EPEL depending on release. Both `uuid-devel` and `libuuid-devel` are listed, which can be redundant or release-dependent.

Test signals: ndctl `meson setup build` should find all required dependencies on RHEL/CentOS/Fedora-like targets.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/redhat/main.yml -->
