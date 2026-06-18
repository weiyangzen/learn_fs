# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/azure.yml

Purpose: discovers Azure managed disks to use as LVM physical volumes.

Important APIs/types/functions: `find` under `/dev/disk/azure/scsi1` and looped `set_fact`.

Control flow: enumerates managed disk symlinks and appends all paths except `data_device` to `physical_volumes`.

State/persistence behavior: Ansible fact mutation only.

Dependencies/integration: relies on Azure disk symlink layout and `data_device` being comparable to found paths.

Risks/test signals: path mismatch between `data_device` and Azure symlink can fail exclusion. Test signal is expected device list before LVM creation.
