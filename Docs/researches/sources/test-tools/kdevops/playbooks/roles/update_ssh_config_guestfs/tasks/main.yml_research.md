# sources/test-tools/kdevops/playbooks/roles/update_ssh_config_guestfs/tasks/main.yml

Purpose: manages the controller user's OpenSSH config include directive for guestfs-generated kdevops SSH configs.

Important APIs/types/functions: `stat`, `lineinfile` in check mode, `meta: end_play`, `replace`, `blockinfile`, and `file`.

Control flow: checks for `~/.ssh/config`, detects whether the current include and `kdevops_version` comment already exist, exits early when fixed, removes stale include/comment/blank lines otherwise, inserts a managed include block at the beginning, and ensures permissions.

State/persistence behavior: mutates `~/.ssh/config` on localhost and can remove broad lines matching kdevops comments/includes.

Dependencies/integration: depends on `kdevops_version` and OpenSSH include behavior.

Risks/test signals: regex removal may delete user comments containing `kdevops`; replacing all blank lines can compact user formatting. Test signals are a single managed include block and mode `0600`.
