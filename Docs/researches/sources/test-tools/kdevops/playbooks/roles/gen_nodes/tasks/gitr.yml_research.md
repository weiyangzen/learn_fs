# sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/gitr.yml

## Purpose
Main task orchestration for the `gen_nodes` role, which renders kdevops node definitions, Terraform inputs, guestfs/libvirt XML support, and workflow-specific node subsets. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Initialize the enabled nodes list for gitr`, `Expand the gitr node list to include -dev nodes`, `Add the kdevops NFS server to the enabled nodes list`, `Add an iSCSI target to the enabled nodes list`, `Generate the kdevops nodes file using {{ kdevops_nodes_template }}`. Important modules/directives include `all_generic_nodes`, `dest`, `force`, `gitr_enabled_nodes`, `mode`, `node_template`, `nodes`, `set_fact`, `src`, `template`, `vars`, `when`; plus 1 more. Key variable inputs observed in this file include `all_generic_nodes`, `gitr_enabled_nodes`, `gitr_enabled_test_groups`, `kdevops_nodes`, `kdevops_nodes_template`, `node_template`, `topdir_path`. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Initialize the enabled nodes list for gitr`, `Expand the gitr node list to include -dev nodes`, `Add the kdevops NFS server to the enabled nodes list`, `Add an iSCSI target to the enabled nodes list`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `template`. Notable path references include `/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation.
