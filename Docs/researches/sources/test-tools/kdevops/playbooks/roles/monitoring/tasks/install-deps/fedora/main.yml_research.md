<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/fedora/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/fedora/main.yml

Purpose: installs monitoring runtime dependencies on fedora targets, split between common Python plotting support, folio migration support, and memory fragmentation eBPF support.

Important APIs/types/functions: modules `ansible.builtin.dnf`; variables/facts `become_method`; tasks `Install monitoring Python dependencies`, `Install folio migration monitoring dependencies`, `Install memory fragmentation monitoring dependencies`.

Control flow: Uses the `dnf` module to install Python 3, matplotlib/numpy-style plotting packages, `stress-ng` for folio migration workloads, and BCC/eBPF packages when the corresponding monitor flags are enabled. Debian updates apt cache first.

State and persistence behavior: Mutates system package state only; no monitoring data is created here.

Dependencies and integration points: Included by `install-deps/main.yml` based on distribution. Depends on package names available in the target distro repositories.

Risks: Package names differ by distro and kernel/BCC packaging can be fragile. Missing debugfs/BCC kernel support will not be caught by package install alone.

Test signals: Signals are successful idempotent package install and later ability to import matplotlib and BCC and run monitor scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/fedora/main.yml -->
