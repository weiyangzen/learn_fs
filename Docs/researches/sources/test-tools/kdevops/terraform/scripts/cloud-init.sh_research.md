# sources/test-tools/kdevops/terraform/scripts/cloud-init.sh

Purpose: Terraform-rendered cloud-init shell script for kdevops hosts. It currently gates user-data execution and optionally reconfigures SSH to a non-default port.

Important variables are Terraform-substituted `user_data_log_dir`, `user_data_enabled`, `new_hostname`, and `ssh_config_port`. The helper `run_cmd_admin()` executes commands, logs success or failure with timestamps to `admin.txt`, and propagates failures under `set -e`.

Control flow creates the log directory, exits early unless user data is enabled, then checks whether the SSH port differs from 22. For alternate ports it edits `sshd_config`, adjusts SELinux port context when possible, opens firewalld or ufw rules when active, and restarts `sshd`.

State mutations are significant: filesystem logs, SSH daemon config, SELinux policy ports, firewall rules, and service restart. Integration points are Terraform template interpolation, distro package managers, systemd, SELinux tools, and cloud-init execution. Risks include unquoted variables, command logging through `$@`, package-manager assumptions, `sshd` service naming variance, and unused `NEW_HOSTNAME`. Tests should run shellcheck/template checks and containerized dry runs for RHEL-like and Ubuntu-like hosts.
