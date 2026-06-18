# sources/test-tools/kdevops/playbooks/host_vars/debian13-ai-btrfs-default-dev.yml

Purpose: host variable profile for an AI/Milvus benchmark node using `btrfs` storage with `default` block-size labeling. The filename distinguishes baseline/dev inventory variants for the same filesystem matrix entry.

Important APIs/types/functions: defines `ai_docker_fstype`, filesystem-specific mkfs parameters, `filesystem_type`, `filesystem_block_size`, `ai_filesystem`, and `ai_data_device_path`. Values in this file set Docker/Milvus storage behavior rather than executable logic.

Control flow: Ansible loads this host_vars file for the matching inventory host, then AI storage roles consume the variables during install and multi-filesystem benchmark setup.

State/persistence behavior: configures Docker data storage at `/var/lib/docker`. mkfs-related values are `-f`; these can affect on-disk filesystem formatting when storage roles run.

Dependencies/integration: consumed by `ai_install.yml`, `ai_multifs.yml`, and AI storage roles. It maps benchmark result filenames back to storage configuration.

Risks/test signals: wrong host_vars binding can benchmark the wrong filesystem or format the wrong Docker data path. Test signals are generated Milvus results carrying the expected filesystem/config name and role logs showing the intended mkfs options.
