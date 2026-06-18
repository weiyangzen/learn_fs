# sources/test-tools/kdevops/playbooks/roles/ai_milvus_storage/tasks/main.yml

Purpose: Formats and mounts dedicated Milvus data storage with filesystem parameters inferred from variables or node names.

Key APIs and flow: When `ai_milvus_storage_enable` is true, the role installs filesystem tools, validates the device, checks current mount state, creates the mount point, optionally derives fstype and XFS/ext4 parameters from `inventory_hostname`, formats XFS/Btrfs/ext4, mounts and persists fstab, creates Milvus `data`, `etcd`, and `minio` directories, and reports the selected filesystem.

State, dependencies, integration: Destructively formats `ai_milvus_device` on first setup and persists mounts. It integrates with AI benchmark node naming conventions such as `xfs`, `64k`, `4ks`, `ext4`, and `bigalloc`.

Risks and test signals: Inventory-name parsing is brittle; whitespace in folded Jinja facts can leak into command values; mounted devices skip format validation; owner is root for Milvus directories. Tests should validate command rendering for XFS sizes, ext4 bigalloc, Btrfs, mounted idempotence, and absent devices.
