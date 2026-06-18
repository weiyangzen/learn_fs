# sources/test-tools/kdevops/terraform/datacrunch/Kconfig

## Purpose
This Kconfig fragment exposes DataCrunch Terraform menus and configuration for compute, OS image, identity/access, API credential file, and optional OS-NVMe volume preservation.

## Important APIs, Types, And Functions
It sources `terraform/datacrunch/kconfigs/Kconfig.compute`, `Kconfig.images`, and `Kconfig.identity`. `TERRAFORM_DATACRUNCH_KEEP_VOLUMES` controls whether OS-NVMe volumes are preserved and cached; its default is driven by whether the `KEEP` make variable is set. `TERRAFORM_DATACRUNCH_API_KEY_FILE` stores the credentials file path, defaulting to `~/.datacrunch/credentials`.

## Control Flow
The file is guarded by `if TERRAFORM_DATACRUNCH`. Menus are shown first, followed by volume-cache and credential path options. Help text documents cost tradeoffs and cache location.

## State And Persistence
Selections persist in `.config` and generated outputs. Volume cache behavior maps to files under `~/.cache/kdevops/datacrunch/$KDEVOPS_HOSTS_PREFIX.yml` via wrapper scripts. Credential file path points to external secret material but does not store the secret in Kconfig.

## Dependencies And Integration Points
It integrates with DataCrunch Terraform modules, apply/destroy wrapper scripts, `volume_cache.py`, and `extract_api_key.py`. It also uses Kconfig `$(shell, ...)` to reflect Make variable state.

## Risks And Test Signals
The `KEEP`-derived default is environment-dependent and can surprise users if stale cache files incur charges. The help text describes a legacy `datacrunch_api_key` key while extractor also requires `client_id`. Tests should verify defconfig behavior with and without `KEEP`, generated YAML values, wrapper interpretation of `.config`, and credential-file path expansion.
