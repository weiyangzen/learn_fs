<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml

Source read: complete file, 24 lines, 685 bytes, sha256 `83ad7e6fa5200b97`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml_research.md`.

Purpose: Red Hat family installation of build-linux timing and visualization packages.

Important APIs/types/functions: `ansible.builtin.dnf` installs `time`, `python3-matplotlib`, and `python3-numpy`, each task gated by `kdevops_workflow_enable_build_linux|default(false)|bool`.

Control flow: timing dependencies and visualization dependencies are separate tasks.

State and persistence behavior: changes dnf/rpm package state when the workflow is enabled.

Dependencies and integration: mirrors the Debian/SUSE package intent for build result statistics and plotting.

Risks: package availability may depend on enabled repos. Core kernel build dependencies are out of scope here.

Test signals: on RedHat-family hosts, enabling the workflow should install these packages and allow the downstream summary visualization code to import numpy/matplotlib.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/build_linux/tasks/install-deps/redhat/main.yml -->
