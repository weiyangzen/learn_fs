<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/handlers/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/handlers/main.yml

Purpose: contains the handler that reloads systemd after Nix cache sync service/timer unit files are templated.

Important APIs/types/functions: modules `ansible.builtin.systemd`; variables/facts `daemon_reload`; tasks `reload nginx`, `reload systemd`.

Control flow: `reload systemd` runs `systemctl daemon-reload` when notified by service or timer template tasks.

State and persistence behavior: Mutates systemd manager state only.

Dependencies and integration points: Notified from `nix-cache-mirror/tasks/main.yml`.

Risks: If handler is skipped, newly written units may not be recognized.

Test signals: Signal is daemon-reload execution followed by timer enable/start success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/handlers/main.yml -->
