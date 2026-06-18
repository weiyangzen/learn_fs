# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/main.yml

## Purpose
Main task orchestration for the `extra_volumes` role, which exposes provider-created extra block volumes to guests with stable kdevops device naming and provider-specific setup. It sequences facts, includes, templates, commands, and file/service mutations for that role.

## Important APIs, Types, and Functions
Ansible task entry points include `Include provider-specific tasks`. Important modules/directives include `file`, `include_tasks`, `when`. Includes/imports delegate to `file: "{{ role_path }}/tasks/providers/{{ kdevops_terraform_provider }}.yml`. Key variable inputs observed in this file include `kdevops_terraform_provider`, `role_path`. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Include provider-specific tasks`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `file`. Notable path references include `/tasks/providers/{{`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
