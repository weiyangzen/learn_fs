<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml

Source read: complete file, 8 lines, 215 bytes, sha256 `b47e75c917f94f33`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml_research.md`.

Purpose: defaults for the `btrfs_progs` role. They disable source builds by default and define where btrfs-progs will be cloned, which repository is used, and which branch/tag to build.

Important APIs/types/functions: Ansible variables `btrfs_progs_build`, `btrfs_progs_data`, `btrfs_progs_git`, and `btrfs_progs_version`. The path depends on the broader `data_path` variable supplied by kdevops inventory/workflow configuration.

Control flow: loaded automatically by the role before tasks run. Downstream tasks use `btrfs_progs_build|bool` to decide whether dependency install, git clone, configure, build, and install steps are active.

State and persistence behavior: no host state is changed by this file alone. It determines persistent clone/build state under `{{ data_path }}/btrfs-progs` when enabled.

Dependencies and integration: integrated with `btrfs_progs/tasks/main.yml`, distribution-specific dependency tasks, and any workflow that needs a custom btrfs-progs binary instead of the distro package.

Risks: the default `devel` version tracks a moving upstream branch, so enabled builds are not reproducible unless callers pin `btrfs_progs_version`. `GIT_SSL_NO_VERIFY` in the consuming task reduces transport assurance.

Test signals: an Ansible dry run should show no build activity with defaults; with `btrfs_progs_build=true`, the role should clone to `btrfs_progs_data` and produce an installed `btrfs` binary in the configured bindir.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/btrfs_progs/defaults/main.yml -->
