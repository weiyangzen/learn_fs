# sources/object-store/openstack-swift/swift/common/ring/ring.py

## Purpose
`ring.py` contains the runtime ring data representation and lookup object. `RingData` serializes/deserializes partition-to-device assignments and device metadata. `Ring` loads a serialized ring, reloads when the file changes, hashes account/container/object names to partitions, returns primary nodes, and generates handoff nodes for hinted handoff.

## Important APIs, types, and functions
Module helpers are `calc_replica_count()` for full/fractional replica tables and `normalize_devices()` for legacy replication IP/port defaults. `RingData` exposes `replica_count`, `part_power`, `dev_id_bytes`, `load()`, `from_dict()`, `serialize_v1()`, `serialize_v2()`, `save()`, and `to_dict()`. `Ring` exposes properties for device id bytes, next partition power, part power, version, compressed/raw size, replica count, partition count, device counts, and devices. Lookup methods include `has_changed()`, `get_part()`, `get_part_nodes()`, `get_nodes()`, and `get_more_nodes()`.

## Control flow and state behavior
`RingData.__init__()` normalizes devices, converts assignment rows to arrays, stores part shift, optional next part power/version, and metadata needed for metadata-only loads. V1 serialization writes magic, metadata JSON, and 2-byte assignment rows. V2 writes named sections for metadata, devices, and assignments using `RingWriter`. Loading opens a `RingReader`, dispatches by version through `RING_CODECS`, optionally skips assignments/devices, and records compressed and raw sizes.

`Ring.__init__()` validates global hash configuration, resolves the ring file path, stores reload timing, and forces an initial load. `_reload()` only replaces runtime state if the file changed and the optional validation hook accepts the new data; invalid reloads are ignored after initial load. Bookkeeping counts assigned/weighted devices and distinct regions/zones/IPs with assignments. `get_part()` hashes the request path and shifts the high 32 bits by `part_shift`. `get_more_nodes()` scans deterministic handoff partitions in phases: first unused regions, then zones, then IPs, then any remaining assigned devices.

## Dependencies and integration points
The module depends on `array`, `json`, `struct`, `time`, `os.path.getmtime`, `itertools`, `RingReader`, `RingWriter`, `hash_path`, `validate_configuration`, `md5`, `tiers_for_dev`, and Swift exceptions. Runtime servers and proxy controllers use `Ring` to route account/container/object requests. Ring-builder tooling uses `RingData` for persisted ring output.

## Risks and edge cases
V1 rings only support 2-byte device ids; larger rings need v2. Metadata-only loads must preserve replica count and device-id-byte fields without assignment rows. `has_changed()` relies only on mtime, so content changes without mtime changes are invisible. Runtime reload ignores invalid changed rings, preserving availability but possibly hiding operator mistakes. `get_more_nodes()` only considers assigned devices for early termination, so unassigned weighted devices are excluded until a new ring assigns them. Duplicate primary dev ids are collapsed, which matters for partial/fractional replicas. Hash configuration must be present before construction.

## Test signals
Tests should cover replica count math for fractional tables, legacy device normalization, v1/v2 serialization round trips, metadata-only and include-devices false loads, v1 device-id-size rejection, deterministic saves, validation hook failure on initial and runtime reload, mtime reload behavior, partition hashing, primary-node duplicate filtering and indexes, device/bookkeeping counts, tier data rebuild, handoff ordering across region/zone/IP/device phases, and next-part-power exposure.
