<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Kconfig -->
# sources/test-tools/kdevops/workflows/rcloud/Kconfig

## Purpose
This Kconfig file adds an optional `RCLOUD` workflow to kdevops. It lets users enable the Rust REST API server and configure its bind address, worker count, and Terraform provider build.

## Important Symbols
`RCLOUD` is a top-level bool defaulting to `n`. When enabled, `RCLOUD_SERVER_BIND` is emitted to YAML with default `127.0.0.1:8765`, `RCLOUD_WORKERS` is emitted to YAML with default `4`, and `RCLOUD_ENABLE_TERRAFORM_PROVIDER` defaults to `y`.

## Control Flow and Integration
The `if RCLOUD` block scopes all runtime configuration to enabled deployments. The workflow `Makefile` checks `CONFIG_RCLOUD` and adds `rcloud-build` to `DEFAULT_DEPS`, then uses `CONFIG_RCLOUD_SERVER_BIND` and `CONFIG_RCLOUD_ENABLE_TERRAFORM_PROVIDER` for build/install behavior. Values marked `output yaml` become part of `extra_vars.yaml`, which `src/config/kdevops.rs` later reads.

## State, Persistence, and Dependencies
Kconfig persists deployment intent through generated kdevops configuration. The comments intentionally recommend localhost binding unless authentication is provided. The Terraform provider option assumes a separate `terraform-provider-rcloud` tree and a Go toolchain when enabled.

## Risks and Test Signals
The default Terraform provider build being enabled can make `make` fail on systems without Go even when users only need the API server. Exposing `0.0.0.0:8765` has an explicit security risk because the current API handlers do not enforce authentication. Validation signals are generated YAML values and Makefile behavior under both enabled and disabled `RCLOUD`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Kconfig -->
