# sources/object-store/rustfs/crates/ecstore/src/sets.rs

## Purpose
Defines `Sets`, the pool-level router over multiple `SetDisks` erasure sets. It builds per-set disk groups, hashes object names to sets, forwards storage traits to the chosen set, monitors endpoints, handles multi-set bulk deletes, and heals disk format metadata for a pool.

## Important APIs, Types, And Functions
`Sets::new` constructs the shard layout from disks, endpoints, format metadata, parity, and global lock clients. Routing helpers are `get_hashed_set_index`, `get_disks`, and `get_disks_by_key`. Trait implementations cover `ObjectIO`, `ObjectOperations`, `MultipartOperations`, `HealOperations`, `StorageAPI`, and `NamespaceLocking`. Support functions include `apply_delete_objects_results`, `init_storage_disks_with_errors`, `formats_to_drives_info`, and `new_heal_format_sets`.

## Control Flow
Construction iterates format sets/drives, attaches local distributed disks from global maps when needed, validates disk IDs, builds lock-client sets per host, and spawns `monitor_and_connect_endpoints`. Object operations mostly hash the object key and delegate to one `SetDisks`. `delete_objects` groups input by hashed set, runs bounded concurrent per-set deletes, and writes results back to original order. `heal_format` reconnects endpoints, loads format metadata, finds a quorum reference format, writes missing format files to unformatted disks, closes stale disk handles, and renews disks.

## State And Persistence Behavior
`Sets` owns in-memory `Arc<SetDisks>` shards and a broadcast exit signal. It persists `format.json` during format healing and mutates live disk membership through `renew_disk`. It does not persist object data directly; delegated set operations do.

## Dependencies And Integration Points
This file integrates endpoints, disk initialization, format quorum, global local-disk maps, lock clients, hash utilities, heal commands, and all storage trait surfaces. `ECStore` holds `Vec<Arc<Sets>>` pools and delegates through these routers.

## Risks
Many bucket/list operations remain `unimplemented!()` at this layer, so callers must use `ECStore` or implemented paths. Namespace locking always delegates to `disk_set[0]`, which centralizes lock construction but may be surprising for multi-set pools. Construction assumes format set dimensions match endpoint ordering.

## Test Signals
Tests cover preserving delete result order across out-of-order set batches. Indirect tests in other files cover disk renewal. More tests should cover hash routing stability, distributed local disk substitution, format healing, and namespace lock quorum across lock clients.
