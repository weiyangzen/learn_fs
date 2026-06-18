# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/suse/main.yml

Purpose: SUSE-family dependency setup for sysbench, including distribution facts and Docker tooling.

Important APIs/types/functions: sets SUSE/SLE facts, flags repository capability assumptions, and installs Docker tools through `zypper`.

Control flow: derives generic and SLE-specific release facts, decides whether repo-dependent features are available, then installs Docker-related packages when supported.

State/persistence behavior: changes Ansible facts and package state; no benchmark data is created.

Dependencies/integration: selected by sysbench dependency dispatcher for SUSE OS family. Feeds later MySQL Docker sysbench tasks.

Risks/test signals: SLE version detection and repository presence are fragile across SUSE variants. Test signals are successful zypper install and Docker runtime availability.
