# sources/test-tools/kdevops/playbooks/roles/gen_hosts/tasks/main.yml

## Purpose
Main task orchestration for the `gen_hosts` role, which renders Ansible inventory and workflow host files from kdevops configuration, enabled workflows, and provider state. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Import optional extra_args file`, `Parse declared hosts list when using declared hosts`, `Get our user`, `Get our primary group`, `Check if the inventory file exists already`, `Ensure proper permission on the inventory file`, `Verify Ansible inventory template file exists`, `Set fstests config file variable for {{ fstests_fstyp }}`, `Verify fstest config file exists`, `Infer enabled fstests test section types`, `Infer enabled blktests test section types`, `Debug inferring block test types`; plus 20 more. Important modules/directives include `all_generic_nodes`, `become`, `become_flags`, `become_method`, `blktests_enabled_test_types`, `build_linux_enabled_section_types`, `clean_section_lines`, `command`, `config_prefix`, `debug`, `dest`, `enabled_fs`; plus 53 more. Key variable inputs observed in this file include `ansible_cfg_inventory`, `build_linux_nodes`, `clean_section_lines`, `enabled_fs`, `enabled_fs_sections`, `enabled_fs_sysbench`, `enabled_sysbench_tests`, `fio_tests_node_names`, `fs`, `fs_config_data`, `fs_config_path`, `fs_config_role_path`, `fs_section_variables`, `fstests_fstyp`; plus 22 more. The role-level integration surface is the `gen_hosts` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Import optional extra_args file`, `Parse declared hosts list when using declared hosts`, `Get our user`, `Get our primary group`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `set_fact`, `register`, `template`, `file`. Notable path references include `/.config`, `/extra_vars.json`, `/extra_vars.yaml`, `/extra_vars.yml`, `/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated in inventory generation before playbook execution. It consumes variables from `.config`/extra vars, enabled workflow flags, provider addressing, and Jinja templates under `templates/`. Shell/command integration points observed here include `whoami`, `id -g -n`.

## Risks
The main risks are stale generated inventory, host/group naming transformations, provider address assumptions, and enabled workflow flags diverging from node generation. File-local risk signals: ignored failures can turn hard setup errors into later, less obvious workflow failures; command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; diff generated files against expected fixtures; run downstream inventory parsing or Terraform/libvirt validation.
