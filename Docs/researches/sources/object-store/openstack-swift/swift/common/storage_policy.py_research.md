# sources/object-store/openstack-swift/swift/common/storage_policy.py

## Purpose

This module defines Swift storage policy configuration, validation, lookup, ring loading, and policy-specific behavior. Storage policies are the cluster-wide abstraction that maps object data to different object rings and diskfile implementations, including replicated and erasure-coded storage. The module also owns the process-wide `POLICIES` singleton loaded from `swift.conf`.

## Important APIs, types, and functions

`BindPortsCache` scans all configured object rings and returns the bind ports that belong to the local node IP set. It caches ring file mtimes and metadata-only ring device port sets by ring path, avoiding full ring loads.

`PolicyError` is the main validation exception. `get_policy_string(base, policy_or_index)` and `split_policy_string(policy_string)` encode and decode policy indices in names such as object ring filenames and on-disk directories, using policy zero as the legacy no-suffix form through `get_zero_indexed_base_string()`.

`BaseStoragePolicy` validates common fields: non-negative integer index, name and aliases, deprecation/default flags, registered policy type, ring name, and diskfile module. It supplies name/alias manipulation, `from_config()`, `get_info()`, lazy `load_ring()`, `validate_ring_data()` hook, abstract `quorum`, and `get_diskfile_manager()`. The diskfile manager is loaded through Swift's package resource loader and checked against the policy.

`StoragePolicy` is the replicated policy class registered as `policy_type = replication`; its quorum is `floor(replica_count / 2) + 1` via `quorum_size()`. `ECStoragePolicy` is registered as `erasure_coding`; it validates PyECLib type, data/parity counts, object segment size, duplication factor, and a known-dangerous ISA-L configuration. It constructs an `ECDriver`, calculates EC quorum, exposes EC properties, computes fragment size lazily, validates that the object ring replica count equals `(data + parity) * duplication_factor`, and maps ring node index to backend fragment index.

`StoragePolicyCollection` indexes policies by case-insensitive name and integer index, enforces uniqueness and default/deprecation rules, supplies lookup by name/index/name-or-index, exposes the legacy policy, lazily loads object rings, emits public `/info` policy data, and supports alias add/remove/primary-name changes.

`parse_storage_policies(conf)` builds policy objects from `storage-policy:<index>` sections. `reload_storage_policies()` reads `utils.SWIFT_CONF_FILE`, parses policies, and updates `_POLICIES`; `POLICIES` is a `StoragePolicySingleton` proxy so code that imported `POLICIES` continues to see the current `_POLICIES` object after reload.

## Control flow

At import time `_POLICIES` is initialized by `reload_storage_policies()`, then `POLICIES` is created as a proxy. Config parsing iterates storage-policy sections, selects a policy class from `BaseStoragePolicy.policy_type_to_policy_cls`, maps config option names to constructor parameters, and constructs a collection. Collection validation first checks duplicates/defaults while adding supplied policies, then creates policy zero automatically only if no policies were provided, rejects multi-policy configurations without explicit index zero, rejects all-deprecated configurations, and requires exactly one default when multiple policies exist.

Ring loading is lazy. Services ask `POLICIES.get_object_ring(policy_idx, swift_dir)`, which finds a policy, calls `policy.load_ring(swift_dir)` if necessary, and returns the policy's `object_ring`. EC policies pass `validate_ring_data()` into `Ring()` so invalid replica counts fail during ring load.

## State and persistence behavior

The durable source of truth is `swift.conf` plus ring files under `swift_dir`; this module keeps in-memory policy objects and cached ring objects. `BaseStoragePolicy.object_ring` is loaded once unless tests inject an object ring or callers set ring reload behavior. `BindPortsCache` stores ring mtimes and port sets and refreshes each ring path when mtime changes. Alias mutation methods update both the policy alias list and the collection's `by_name` index, but these runtime mutations are not written back to config.

## Dependencies and integration points

The module integrates with `swift.common.ring.Ring` and `RingData`, `swift.common.utils` config parsing helpers, `swift.common.exceptions.RingLoadError`, and PyECLib (`ECDriver`, `VALID_EC_TYPES`). It is central to proxy, object-server, diskfile, recon, and `/info` behavior because policy index and type affect ring lookup, quorum, diskfile implementation, EC fragment math, object metadata, and operator-visible policy information.

Diskfile integration is pluggable through entry points such as `egg:swift#replication.fs` and `egg:swift#erasure_coding.fs`. Public policy info intentionally omits policy type, diskfile module, and detailed EC parameters unless config output is requested.

## Risks and edge cases

Import-time config parsing can raise `SystemExit` on invalid `swift.conf`, so tests and tools that import this module need controlled config fixtures. `parse_storage_policies()` indexes `policy_type_to_policy_cls` directly; an unknown `policy_type` raises `KeyError` rather than `PolicyError`. Name validation is restrictive because names become HTTP headers; aliases are case-insensitive in collection indexes but stored with original case in the policy.

EC policy correctness is high risk. The ring replica count must exactly match unique fragments times duplication factor; too few or too many replicas break proxy/object assumptions. The `isa_l_rs_vand` parity warning includes a hard validation requirement that affected policies be deprecated. Fragment size calculation deliberately asks PyECLib for segment-sized data even when ranged GETs may not know the full object size; regressions there affect EC range reads.

Policy zero is special throughout name encoding and config defaults. Tests should cover `None`, empty string, string index, integer index, and unknown index lookups to avoid breaking legacy paths.

## Test signals

Tests should exercise empty config default policy creation, multi-policy validation errors, default/deprecated conflicts, duplicate names and indexes, alias lifecycle, policy string encoding/decoding, public vs config `get_info()`, singleton reload behavior, diskfile manager loading/check failures, ring lazy loading, `BindPortsCache` mtime refresh, replicated quorum, EC constructor validation, EC ring replica validation, EC backend index modulo behavior, and known-dangerous EC configuration handling.
