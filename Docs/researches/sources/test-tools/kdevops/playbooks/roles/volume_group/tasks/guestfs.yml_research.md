# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/guestfs.yml

Purpose: discovers extra guestfs/libvirt block devices to use as LVM physical volumes while excluding root and `/data`.

Important APIs/types/functions: `set_fact` for device ID patterns, `fail`, `debug`, `find` under `/dev/disk/by-id`, and looped `set_fact` appending to `physical_volumes`.

Control flow: selects a by-id pattern based on configured bus type, fails if unsupported, reports reserved data device, finds matching symlinks excluding partitions and the data device, and appends found paths.

State/persistence behavior: only updates Ansible `physical_volumes`; LVM mutation happens later.

Dependencies/integration: included by volume group main when `kdevops_enable_guestfs` is true. Depends on libvirt extra storage variables and stable `/dev/disk/by-id` naming.

Risks/test signals: wrong pattern/exclusion can select the wrong disk. Test signals are discovered symlink list and final LVM creation.
