<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/iscsi.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/iscsi.yml

Purpose: creates and mounts an iSCSI-backed filesystem for a new NFS export.

Important APIs/types/functions: modules `ansible.builtin.include_role`, `community.general.open_iscsi`, `ansible.builtin.command`, `ansible.builtin.set_fact`, `community.general.filesystem`, `ansible.posix.mount`; variables/facts `iscsi_add_devname`, `iscsi_add_size`, `tasks_from`, `become_flags`, `become_method`, `rescan`, `cmd`, `changed_when`, `iscsi_device`, `fstype`; tasks `Create an iSCSI LUN for the new export`, `Rescan iSCSI LUNs on the NFS server`, `Rescan iSCSI LUNs on the target node`, `Enumerate available SCSI devices on the NFS server`, `Select the device that matches {{ export_volname }}`.

Control flow: Delegates iSCSI LUN creation/attachment to storage roles, waits for the block device, formats it, and mounts it under the export root.

State and persistence behavior: Persists remote LUN state, local initiator/device state, filesystem, and mount entry.

Dependencies and integration points: Used when `nfsd_export_storage_iscsi` is true. Depends on iSCSI target/initiator role variables and block device discovery.

Risks: Device naming/timing races can format the wrong device if discovery assumptions change. Cleanup is not represented in this task.

Test signals: Signals are visible iSCSI session, expected block device, mounted export, and client mount success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/iscsi.yml -->
