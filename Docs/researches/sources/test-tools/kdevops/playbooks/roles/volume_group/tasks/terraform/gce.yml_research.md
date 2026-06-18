# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/gce.yml

Purpose: discovers Google Compute Engine persistent disks to use as LVM physical volumes.

Important APIs/types/functions: regex `find` under `/dev/disk/by-id` and looped `set_fact`.

Control flow: finds `google-persistent-disk-N` symlinks, excludes the data device and root disk `google-persistent-disk-0`, and appends the rest.

State/persistence behavior: Ansible fact mutation only.

Dependencies/integration: relies on GCE persistent disk naming conventions and `data_device`.

Risks/test signals: hard-coded root/data assumptions can fail if disk numbering changes. Test signal is deterministic candidate list.
