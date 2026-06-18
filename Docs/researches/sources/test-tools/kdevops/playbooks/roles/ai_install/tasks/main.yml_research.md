# sources/test-tools/kdevops/playbooks/roles/ai_install/tasks/main.yml

Purpose: Installs host prerequisites for the AI benchmark workflow.

Key APIs and flow: Includes `create_data_partition`, optionally includes `common` for user/group inference, ensures `data_path` ownership, includes optional extra vars, installs Docker packages and group membership when Docker Milvus is enabled, installs Python benchmark and graphing dependencies with pip, installs filesystem utilities for XFS/Btrfs, and creates the benchmark results directory.

State, dependencies, integration: Mutates packages, Python environment, user groups, data directories, and benchmark result directory. Integrates variables for Docker deployment, filesystem type, graphing, and data ownership.

Risks and test signals: Pip dependencies install globally unless Ansible config redirects them; extra-vars include always succeeds; adding a user to docker group requires new login to take effect; ext4 utilities are not installed explicitly. Tests should cover Docker disabled, graphing disabled, each filesystem type, and idempotent ownership changes.
