<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/models.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/models.rs

## Purpose
This module defines the JSON contract for rcloud API requests and responses.

## Important Types
`CreateVmRequest` includes `name`, `vcpus`, `memory_mb`, `base_image`, `root_disk_gb`, optional `ssh_user`, and optional `ssh_public_key`. `CreateVmResponse` returns `id`, `name`, and `state`. `VmResponse` returns VM identity, lifecycle state, sizing, and optional `ip_address`. `ListVmsResponse` wraps VM responses. `ImageInfo` and `ListImagesResponse` model available base images.

## Control Flow and Integration
These are passive Serde structs used by Actix extractors and JSON responses in `handlers/vms.rs` and `handlers/images.rs`. Optional fields are skipped when serializing if absent.

## State, Persistence, and Dependencies
The module does not persist state; it defines wire-level data shape. Dependencies are Serde derive traits. Persistent VM data is provided by libvirt through `VmManager` and adapted into these response types.

## Risks and Test Signals
There are no validation attributes, so invalid values are syntactically accepted if they deserialize. Optional SSH public key content can be large and sensitive. API compatibility depends on these field names remaining stable. Tests should cover JSON round trips and invalid payload handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/models.rs -->
