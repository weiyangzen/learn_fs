# sources/test-tools/kdevops/playbooks/roles/volume_group/defaults/main.yml

Purpose: defaults for LVM volume group provisioning.

Important APIs/types/functions: defines guestfs/Terraform booleans, `physical_volumes`, `ebs_volume_ids`, and `tmp_device`.

Control flow: no executable flow; values seed provider-specific enumeration and final LVM creation.

State/persistence behavior: no direct state.

Dependencies/integration: consumed by `tasks/main.yml` and provider/guestfs task files.

Risks/test signals: empty `physical_volumes` is expected initially but must be populated before LVM creation. Test signal is final list content.
