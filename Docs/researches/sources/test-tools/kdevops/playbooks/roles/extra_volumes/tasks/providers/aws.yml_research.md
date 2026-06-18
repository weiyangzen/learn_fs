# sources/test-tools/kdevops/playbooks/roles/extra_volumes/tasks/providers/aws.yml

## Purpose
Provider-specific implementation for the `extra_volumes` role. It adapts the generic extra-volume workflow to the selected cloud provider's device discovery and naming model.

## Important APIs, Types, and Functions
Ansible task entry points include `Install tmpfiles.d configuration for /dev/disk/kdevops/`, `Create /dev/disk/kdevops/ directory using tmpfiles`, `Extract the "extra volumes" map`, `Install the script that creates symlinks in /dev/disk/kdevops`, `Create the "extra volumes" udev rule`, `Force the target node to reload its udev ruleset and trigger block devices`. Important modules/directives include `become`, `binary_path`, `changed_when`, `cloud.terraform.terraform_output`, `command`, `delegate_to`, `dest`, `format`, `group`, `mode`, `name`, `owner`; plus 8 more. Key variable inputs observed in this file include `terraform_binary_path`, `terraform_output`, `topdir_path`. The role-level integration surface is the `extra_volumes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
Ansible executes tasks in file order. The path starts with `Install tmpfiles.d configuration for /dev/disk/kdevops/`, `Create /dev/disk/kdevops/ directory using tmpfiles`, `Extract the "extra volumes" map`, `Install the script that creates symlinks in /dev/disk/kdevops`, then continues through conditional branches controlled by `when` expressions, registered command results, loops, and included task files. Later tasks often depend on facts or files established earlier in the same role.

## State and Persistence Behavior
The file mutates target or localhost state through `register`, `template`, `systemd`. Notable path references include `/dev/disk/kdevops`, `/dev/disk/kdevops/`, `/etc/tmpfiles.d/kdevops-disk.conf`, `/etc/udev/rules.d/99-aws-ebs.rules`, `/terraform/aws`, `/usr/local/bin/udev-ebs-tagger`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated after Terraform/provider provisioning. AWS consumes Terraform output and udev templates; other providers are placeholders in this slice. Shell/command integration points observed here include `systemd-tmpfiles --create /etc/tmpfiles.d/kdevops-disk.conf`, `udevadm control --reload && udevadm trigger --subsystem-match=block --action=add`.

## Risks
The main risk is provider-specific block device naming drift; incorrect udev or Terraform mapping can point tests at the wrong disk. File-local risk signals: command tasks rely on exact distro command output and idempotence annotations.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; check target systemd unit state after the role.
