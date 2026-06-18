# sources/test-tools/kdevops/playbooks/roles/gen_nodes/tasks/main.yml

## Purpose
Main task orchestration for the `gen_nodes` role, which renders kdevops node definitions, Terraform inputs, guestfs/libvirt XML support, and workflow-specific node subsets. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Get our user`, `Get our primary group`, `Create guestfs directory`, `Create nixos directory`, `Verify Ansible nodes template file exists {{ kdevops_nodes_template_full_path }}`, `Set generic nodes array`, `Set generic nodes array on dual baseline and dev systems`, `Set builder nodes array`, `Set iscsi_nodes list`, `Add an iSCSI target`, `Set nfsd_nodes list`; plus 80 more. Important modules/directives include `ai_enabled_section_types`, `ai_multifs_enabled_configs`, `all_fs_configs`, `all_generic_nodes`, `all_nodes`, `args`, `become`, `become_flags`, `become_method`, `blktests_enabled_test_types`, `btrfs_configs`, `btrfs_std_enabled`; plus 108 more. Includes/imports delegate to `name: gen_nodes`, `name: gen_nodes`, `name: gen_nodes`. Key variable inputs observed in this file include `ai_enabled_section_types`, `all_fs_configs`, `all_generic_nodes`, `all_nodes`, `blktests_enabled_test_types`, `build_linux_enabled_section_types`, `builder_nodes`, `clean_section_lines`, `clean_section_lines_without_fsname`, `config_block_test_types`, `config_mmtests_test_types`, `config_sections_targets`, `config_selftests_test_types`, `config_val`; plus 48 more. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Get our user`, `Get our primary group`, `Create guestfs directory`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`, `lineinfile`. Notable path references include `/.config`, `/bin/bash`, `/extra_vars.json`, `/extra_vars.yaml`, `/extra_vars.yml`, `/guestfs/{{`, `/python/gen_pcie_passthrough_guestfs_xml.py`, `/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible. Shell/command integration points observed here include `whoami`, `id -g -n`, `timedatectl show -p Timezone --value`, `|`, `set -o pipefail && ss -ltn | grep ':{{ (libvirt_gdb_baseport | int) + (idx | int) }} '`.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates. File-local risk signals: reboot timing can mask failures or leave dependent roles running against a node that has not fully converged; ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations; text edits to system config can drift when upstream distro defaults change.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation; verify block-device and mount topology before and after the run.
