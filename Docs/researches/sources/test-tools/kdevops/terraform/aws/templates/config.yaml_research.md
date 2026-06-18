# sources/test-tools/kdevops/terraform/aws/templates/config.yaml

## Purpose
This small cloud-init YAML template configures hostname behavior and the default SSH user for AWS guests launched by kdevops Terraform.

## Important APIs, Types, And Functions
The file is declarative YAML. It sets `preserve_hostname: false`, `manage_etc_hosts: false`, `hostname: ${new_hostname}`, and `system_info.default_user.name: ${ssh_config_user}`. The `${...}` placeholders are intended for Terraform/template substitution.

## Control Flow
There is no executable control flow. A provisioning layer renders the template with a target hostname and SSH username, then passes it as cloud-init user-data or merged cloud configuration.

## State And Persistence
The rendered configuration affects guest-local persistent state: hostname and default user configuration. The template itself stores no secrets.

## Dependencies And Integration Points
It depends on cloud-init semantics and the surrounding Terraform/template engine that supplies `new_hostname` and `ssh_config_user`. It integrates with AWS instance provisioning and kdevops SSH access setup.

## Risks And Test Signals
If placeholders are not substituted, guests may receive literal `${...}` values. Disabling `manage_etc_hosts` may interact with distro defaults. Tests should render the template with representative values, validate YAML syntax, boot a cloud image, and verify hostname/default user behavior.
