# sources/test-tools/kdevops/playbooks/roles/gen_nodes/defaults/main.yml

## Purpose
Defines default variables for the `gen_nodes` role, which renders kdevops node definitions, Terraform inputs, guestfs/libvirt XML support, and workflow-specific node subsets. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation; verify block-device and mount topology before and after the run.
