# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/redhat/main.yml

Purpose: Red Hat-family dependency setup for sysbench, mainly enabling repositories and installing Docker/sysbench packages.

Important APIs/types/functions: includes `codereadyrepo`, installs `epel-release` when appropriate, and installs a `packages` list through `dnf`.

Control flow: enables CodeReady, optionally enables EPEL, then installs Docker and sysbench dependency packages.

State/persistence behavior: changes repository availability and system package state.

Dependencies/integration: selected by `install-deps/main.yml` for RedHat OS family. Depends on distro-specific repository roles/tasks and package manager metadata.

Risks/test signals: repository enabling can vary across RHEL, CentOS Stream, and clones. Test signals are dnf success and later Docker/sysbench command availability.
