# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/oci.yml

## Purpose
Provider-specific implementation for the `extra_volumes` role. It adapts the generic extra-volume workflow to the selected cloud provider's device discovery and naming model.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes this file in order as an included task file. Its behavior is primarily controlled by `when` expressions and variables inherited from the role defaults and inventory.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
