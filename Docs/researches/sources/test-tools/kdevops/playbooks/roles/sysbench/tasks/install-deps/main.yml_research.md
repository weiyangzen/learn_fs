# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/main.yml

Purpose: dispatcher for OS-specific sysbench dependency installation.

Important APIs/types/functions: includes role `pkg`, then conditionally includes `debian/main.yml`, `suse/main.yml`, or `redhat/main.yml` based on `ansible_facts.os_family`.

Control flow: runs generic package role first, then branches by normalized OS family.

State/persistence behavior: direct persistent changes are delegated to included package tasks.

Dependencies/integration: depends on gathered facts and role-relative task paths. It is included by sysbench role setup before database deployment.

Risks/test signals: unsupported or differently named OS families silently skip all OS-specific setup. Test signals are Ansible include selection and successful package availability after the branch.
