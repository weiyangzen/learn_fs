# Research: sources/test-tools/kdevops/playbooks/roles/guestfs/tasks/bringup/main.yml

`sources/test-tools/kdevops/playbooks/roles/guestfs/tasks/bringup/main.yml` is a role task flow in the kdevops `guestfs` role. Role context: provisions, boots, destroys, and inspects libvirt guestfs virtual machines. The file is 181 lines / 6793 bytes and was read in full for this report.

## Purpose

This Ansible file drives `guestfs` role task flow behavior through 23 named task(s). The key task sequence is: `List defined libvirt guests`, `Debug defined VMs`, `Provision each target node`, `Set the pathname of the ssh directory for each target node`, `Set the pathname of the ssh key for each target node`, `Generate ssh keys for each target node`, `Create the ssh key directory on the control host`, `Generate fresh keys for each target node`, `Set the pathname of the root disk image for each target node`, `Create the storage pool directory for each target node`, plus 13 more.

## Important APIs, Types, And Functions

The primary Ansible interfaces are `LIBVIRT_DEFAULT_URI`, `ansible.builtin.command`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.include_tasks`, `ansible.builtin.set_fact`, `ansible_callback_diy_runner_on_ok_msg`, `argv`, `cmd`, `command`, `community.libvirt.virt`, `creates`, `debug`, `file`, plus 15 more. Variables and facts referenced or defined include `[ "virt-sysprep", "-a", root_image, "--hostname", inventory_hostname, "--ssh-inject", "kdevops:file:" + ssh_key + ".pub", "--timezone", host_timezone.stdout ] + ( [ "--run-command", "sed -i '/^#*Port /d' /etc/ssh/sshd_config", "--append-line", "/etc/ssh/sshd_config:Port " + (ansible_cfg_ssh_port`, `ansible_callback_diy.result.output.msg`, `argv`, `base_image`, `become`, `become_method`, `block`, `bootlinux_9p_host_path`, `cmd`, `command`, `creates`, `debug`, `delegate_to`, `environment`, `file`, `file_type`, `guestfs_path`, `hostvars['localhost']['defined_vms']['list_vms']`, plus 29 more. Registered result objects include `defined_vms`, `host_timezone`, `passthrough_devices`. Included roles/tasks/templates or named dependencies visible in the file include `{{ role_path }}/tasks/bringup/extra-disks.yml`, `{{ role_path }}/tasks/bringup/largeio.yml`.

## Control Flow

Execution follows Ansible task order. Conditional branches are controlled by `when` expressions, distribution selectors, feature flags, and registered command results. Notable conditions are none found. The file also uses Ansible `block` structure for grouped operations and, where present, rescue/error-recovery behavior. Loops expand repeated package, host, disk, result, or service operations over inventory or variable-provided lists.

## State And Persistence

Persistent effects visible from this file target `{{ ssh_key_dir }}`, `{{ storagedir }}/{{ inventory_hostname }}`, `{{ storagedir }}/{{ inventory_hostname }}/extra{{ item }}.{{ libvirt_extra_drive_format }}`, `{{ bootlinux_9p_host_path }}`. State changes are delegated to Ansible modules, so idempotency depends on module semantics, `creates` guards, `changed_when`, `failed_when`, and the external commands used. Facts set with `set_fact` live for the current play and feed later role tasks; files, packages, services, mounts, libvirt resources, certificates, and benchmark outputs persist on the controller or managed hosts as directed by each task.

## Dependencies And Integration Points

The file integrates with role `guestfs`, inventory variables, Ansible facts, optional `extra_vars` files, and the kdevops top-level paths such as `topdir_path` when referenced. External integration points inferred from modules and commands include `LIBVIRT_DEFAULT_URI`, `ansible.builtin.command`, `ansible.builtin.file`, `ansible.builtin.find`, `ansible.builtin.include_tasks`, `ansible.builtin.set_fact`, `ansible_callback_diy_runner_on_ok_msg`, `argv`, `cmd`, `command`, `community.libvirt.virt`, `creates`, `debug`, `file`, `file_type`, `label`, `msg`, `name`, plus 13 more. For install-deps files, package manager behavior is distribution-specific and selected by the parent include file.

## Risks And Edge Cases

command/shell tasks can be non-idempotent unless guarded by `creates`, return-code checks, or explicit changed/failed conditions; privileged operations depend on sudo/root access and can leave host-level state behind; controller-local paths and permissions must match the invoking user; incorrect feature flags or distribution facts can skip required setup.

## Test Signals

Useful validation signals are Ansible syntax-check for this role, running the role with `--check` where modules support it, and exercising the feature tags/conditions that import this file. Runtime confirmation should inspect registered results, created files/directories, package/service state, and any debug/status tasks emitted by the role.
