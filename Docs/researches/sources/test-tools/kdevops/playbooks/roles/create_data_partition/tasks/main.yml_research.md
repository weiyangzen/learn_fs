<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml

Source read: complete file, 55 lines, 1985 bytes, sha256 `9c497aeebb751c1b`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml_research.md`.

Purpose: wrapper role that resolves the data device and invokes generic partition creation for the kdevops data filesystem.

Important APIs/types/functions: `include_role: common`, terraform `output -json block_device_map`, `from_json`, `with_dict`, `set_fact data_volume_id/data_device`, and `include_role: create_partition` with mapped `disk_setup_*` vars.

Control flow: optionally infer user/group through common; on AWS terraform, query block-device map on localhost, find `/dev/sdf`, convert the EBS volume id into the NVMe serial naming pattern, scan `ansible_devices` for a matching id link, and override `data_device`; then call `create_partition`.

State and persistence behavior: sets facts for the current role and delegates actual filesystem/mount/permission persistence to `create_partition`.

Dependencies and integration: depends on terraform output layout, AWS NVMe EBS naming, `topdir_path`, `ansible_devices`, and global variables `data_device`, `data_fstype`, `data_label`, `data_fs_opts`, `data_path`, `data_user`, and `data_group`.

Risks: AWS mapping has a FIXME and hard-codes `/dev/sdf`. If volume id matching fails, the role may fall back to an unsafe or unset `data_device`. Terraform command runs once on localhost and assumes current state exists.

Test signals: in AWS terraform inventory, debug `data_volume_id` and resolved `data_device` before formatting; in non-AWS paths, verify the original inventory device reaches `create_partition`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/tasks/main.yml -->
