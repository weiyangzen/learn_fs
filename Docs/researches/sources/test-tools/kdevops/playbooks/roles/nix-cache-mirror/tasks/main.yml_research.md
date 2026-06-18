<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/tasks/main.yml

Purpose: provisions an nginx-backed Nix binary cache mirror/proxy plus a systemd timer for cache synchronization.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.fail`, `ansible.builtin.package`, `ansible.builtin.file`, `ansible.builtin.template`, `ansible.builtin.command`, `ansible.builtin.systemd`, `ansible.posix.firewalld`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `msg`, `changed_when`, `enabled`, `daemon_reload`, `notify`, `failed_when`, `port`; tasks `Import optional extra_args file`, `Fail if nix cache mirror is enabled but user is not root`, `Install nginx for Nix cache mirror`, `Create Nix cache mirror directories`, `Template nginx cache configuration for Nix cache mirror`.

Control flow: Loads extra vars, fails non-root use, installs nginx/curl, creates cache directories owned by `www-data`, templates nginx cache/site config, enables the site, removes default site, validates nginx, starts/reloads nginx, templates sync service/timer, starts the timer, and optionally opens firewalld.

State and persistence behavior: Persists cache directories, nginx configuration, systemd service/timer units, enabled services, and firewall rules.

Dependencies and integration points: Depends on nginx, curl, systemd, templates, root privileges, and `install_nix_cache_mirror`.

Risks: Hard-coded `www-data` owner can be wrong outside Debian-style systems. Firewall opening is tied to `linux_mirror_nfs`. Nginx site paths vary by distro.

Test signals: Signals are `nginx -t`, active nginx, active timer, reachable HTTP port, and cache directory writes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/tasks/main.yml -->
