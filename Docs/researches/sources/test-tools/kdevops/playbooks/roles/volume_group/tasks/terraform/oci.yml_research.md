# sources/test-tools/kdevops/playbooks/roles/volume_group/tasks/terraform/oci.yml

Purpose: discovers Oracle Cloud block volumes to use as LVM candidates while excluding root and data devices.

Important APIs/types/functions: `stat` of `/dev/oracleoci/oraclevda` and `data_device`, `set_fact` parsing `lnk_source`, and iteration over `ansible_devices`.

Control flow: resolves root device name, resolves data device name, then appends `/dev/<device>` for `ansible_devices` entries whose model is `BlockVolume` and not root/data.

State/persistence behavior: Ansible fact mutation only.

Dependencies/integration: depends on OCI device symlinks and gathered hardware facts.

Risks/test signals: `lnk_source.split('/dev/').1` is brittle if stat output shape changes. Test signals are correct root/data exclusion and non-empty extra volume list.
