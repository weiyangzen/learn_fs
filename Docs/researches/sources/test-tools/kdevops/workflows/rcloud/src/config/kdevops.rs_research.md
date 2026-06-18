<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/kdevops.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/config/kdevops.rs

## Purpose
This module parses kdevops `extra_vars.yaml` and environment overrides into a typed `KdevopsConfig` used by rcloud.

## Important Types and Functions
`KdevopsConfig` stores libvirt URI, storage pool path, base images directory, optional network bridge, optional server bind, optional worker count, optional SSH user and public key path, plus flattened extra YAML. `load(kdevops_root)` reads `extra_vars.yaml`, parses it with Serde YAML, resolves required storage and image paths, applies selected `RCLOUD_*` environment overrides, and returns the config. `get_string` and `get_usize` extract simple YAML values.

## Control Flow
The loader prioritizes environment variables for libvirt URI, storage pool, base images, network bridge, server bind, and workers. It falls back to kdevops YAML keys such as `kdevops_storage_pool_path`, `libvirt_storage_pool_path`, `guestfs_base_image_dir`, and `libvirt_bridge_name`. Missing storage pool or base image directory is fatal.

## State, Persistence, and Dependencies
Persistent state is read from `extra_vars.yaml`; no writes occur. Dependencies include `anyhow`, `serde`, `serde_yaml`, filesystem reads, and environment variables.

## Risks and Test Signals
SSH user and key file are read only from YAML, not environment variables. `extra` stores the whole YAML after values are already inspected. String-only extraction ignores YAML scalar types that are not strings. The included unit test creates a temporary `extra_vars.yaml` and validates core path and bridge parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/config/kdevops.rs -->
