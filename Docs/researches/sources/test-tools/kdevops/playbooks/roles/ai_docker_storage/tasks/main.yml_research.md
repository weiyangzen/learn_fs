# sources/test-tools/kdevops/playbooks/roles/ai_docker_storage/tasks/main.yml

Purpose: Prepares a dedicated filesystem for Docker storage used by AI/Milvus deployments.

Key APIs and flow: When `ai_docker_storage_enable` is true, it installs filesystem tools, validates `ai_docker_device`, checks whether the mount point is already mounted, creates the mount point, formats the device as XFS/Btrfs/ext4 according to variables, mounts it with `defaults,noatime`, persists it in fstab, checks/stops Docker if active, sets `/var/lib/docker` permissions when applicable, and reports completion.

State, dependencies, integration: Highly stateful and destructive on first run because it formats the target block device. Integrates Linux filesystems, mount/fstab, systemd Docker service, and kdevops AI storage variables.

Risks and test signals: Incorrect device variables can destroy data; `ignore_errors` on Docker stop may hide failures; mountpoint check skips formatting if already mounted, regardless of fstype/options. Tests should use check mode or loop devices to validate format command selection, fstab idempotence, and mounted/unmounted paths.
