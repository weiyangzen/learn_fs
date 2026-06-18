# sources/test-tools/kdevops/playbooks/linux-mirror.yml

Purpose: installs local Git, Nix cache, and Docker mirrors using systemd timers/roles to accelerate kdevops workflow dependencies.

Important APIs/types/functions: localhost play runs roles `linux-mirror`, optionally `nix-cache-mirror` when `install_nix_cache_mirror` is true, and `docker-mirror`.

Control flow: configure Linux Git mirror first, optionally configure Nix binary cache mirror, then configure Docker mirror.

State/persistence behavior: creates mirror repositories/caches, service units, timers, and local storage on the controller.

Dependencies/integration: supports workflows that clone Linux or pull container/Nix artifacts, and pairs with `docker-mirror.yml` for tag-specific Docker operations.

Risks/test signals: mirror storage can grow large and stale. Test signals are active timers/services, reachable mirror endpoints, and successful workflow downloads using local mirrors.
