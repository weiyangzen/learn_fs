<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/defaults/main.yml

Purpose: defines Nix cache mirror enablement, port, upstream cache, local cache path, and nginx configuration paths.

Important APIs/types/functions: variables/facts `nix_cache_mirror_path`, `nix_cache_mirror_port`, `nix_cache_upstream_url`, `nix_cache_mirror_nginx_conf_path`, `nix_cache_mirror_nginx_enabled_path`.

Control flow: Defaults are read by the mirror tasks and templates.

State and persistence behavior: No direct state; controls nginx and systemd artifact locations.

Dependencies and integration points: Used when workflows want a local binary cache proxy/mirror.

Risks: Incorrect paths can conflict with distro nginx layout or permissions.

Test signals: Signals are templates rendering the configured port/upstream/path values.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/defaults/main.yml -->
