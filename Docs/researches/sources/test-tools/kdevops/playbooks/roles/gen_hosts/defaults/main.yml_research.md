# sources/test-tools/kdevops/playbooks/roles/gen_hosts/defaults/main.yml

## Purpose
Defines default variables for the `gen_hosts` role, which renders Ansible inventory and workflow host files from kdevops configuration, enabled workflows, and provider state. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `gen_hosts` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated in inventory generation before playbook execution. It consumes variables from `.config`/extra vars, enabled workflow flags, provider addressing, and Jinja templates under `templates/`.

## Risks
The main risks are stale generated inventory, host/group naming transformations, provider address assumptions, and enabled workflow flags diverging from node generation. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation.
