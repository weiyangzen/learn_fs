<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/heal_commands.rs -->
# sources/object-store/rustfs/crates/madmin/src/heal_commands.rs

Purpose: `heal_commands.rs` defines serializable admin/result models for healing operations.

Important APIs/types/functions: `HealItemType` is a string alias. `HealDriveInfo` contains drive UUID, endpoint, and state. `Infos` wraps `drives` as a vector of drive info. `HealResultItem` contains result id (`resultId`), item type (`type`), bucket/object/version identifiers, detail, erasure-coding block counts, disk/set counts, before/after drive info, and object size.

Control flow: no runtime logic exists; serde derive handles field mapping and default construction.

State and persistence behavior: these are DTOs. `Default` yields empty strings, zero numeric counts, and empty drive lists. They do not validate consistency between data/parity blocks, disk count, or before/after states.

Dependencies and integration points: depends on `serde`. `rg` shows `HealResultItem` and `HealDriveInfo` are consumed throughout `ecstore` heal paths, peer S3 clients, set/disk healing, config storage tests, and store APIs. Field names appear designed for admin API compatibility.

Risks: numeric fields use `usize`, which can vary by platform width and may not be ideal for stable wire/API contracts. The `type` JSON field is represented by `heal_item_type` to avoid Rust keyword conflict. Absence of validation means producers must populate coherent counts and drive states. `version_id` is a plain string, so missing version and empty version are indistinguishable.

Test signals: there are no direct tests in this file. Integration tests in healing modules should verify JSON/msgpack compatibility, populated before/after drive states, and object-size/count correctness.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/heal_commands.rs -->
