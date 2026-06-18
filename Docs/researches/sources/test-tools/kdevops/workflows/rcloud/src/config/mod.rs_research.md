<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/mod.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/config/mod.rs

## Purpose
This module defines the application-level configuration consumed by the rcloud server, VM manager, and health/status endpoints.

## Important Types and Functions
`AppConfig` contains `ServerConfig`, `kdevops_root`, libvirt URI, storage pool path, base images directory, network bridge, SSH user, SSH public key file, and `VmDefaults`. `ServerConfig` defaults to `127.0.0.1:8765` and 4 workers. `VmDefaults` defaults to `raw` format and `virtio` driver. `AppConfig::load()` determines `KDEVOPS_ROOT` or current directory, loads `KdevopsConfig`, maps values into path types, and applies defaults. `xml_template_path()` points at the guestfs Q35 XML template in kdevops.

## Control Flow
Configuration loading is synchronous at process startup in `main.rs`. Errors are propagated with context but `main.rs` currently panics via `expect` if loading fails.

## State, Persistence, and Dependencies
The module reads persistent kdevops config through `config/kdevops.rs` and environment variables. It stores configuration in memory and clones it into handlers and the VM manager.

## Risks and Test Signals
`VmDefaults` is not yet used by disk/XML generation, so the configured defaults may not affect runtime behavior. The network bridge fallback is `default` if `KdevopsConfig.network_bridge` is absent, while the lower-level kdevops config defaults to `virbr0`, so behavior depends on where absence is resolved. Tests should cover missing files, environment overrides, and default propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/mod.rs -->
