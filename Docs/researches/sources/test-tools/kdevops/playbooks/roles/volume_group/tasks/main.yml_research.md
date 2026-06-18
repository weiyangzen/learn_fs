# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/main.yml

Purpose: creates an LVM volume group from provider-discovered extra block devices.

Important APIs/types/functions: `gather_facts` hardware subset, package install `lvm2`, conditional includes for guestfs or Terraform provider tasks, `fail`, and `community.general.lvg`.

Control flow: gathers hardware facts, installs LVM support, enumerates devices through guestfs or Terraform provider-specific tasks, fails if no candidates remain, and creates the requested volume group.

State/persistence behavior: installs `lvm2` and writes LVM metadata to selected physical volumes and volume group.

Dependencies/integration: depends on `volume_group_name`, `physical_volumes`, provider variables, root privileges, and `community.general`.

Risks/test signals: destructive LVM metadata on wrong devices is the primary risk. Test signals are non-empty `physical_volumes` and successful `vgs`/`lvs` visibility.
