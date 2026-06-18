# sources/object-store/openstack-swift/swift/common/ring/utils.py

## Purpose

This module is the command-line and serialization utility layer for Swift ring management. It supports ring-builder parsing, ring tier topology construction, device address normalization, local-device matching, device array serialization helpers, and dispersion reporting. The file is not a ring builder itself; it provides the reusable pieces that `swift-ring-builder`, ring validation, and ring serialization code use to keep device dictionaries, device IDs, and placement tiers consistent.

## Important APIs, types, and functions

`BYTES_TO_TYPE_CODE`, `none_dev_id`, `calc_dev_id_bytes`, `resize_array`, `network_order_array`, and `read_network_order_array` define how `replica2part2dev` arrays encode device IDs. `none_dev_id()` reserves the maximum value representable by a device-ID width as the sentinel for an unassigned part. `calc_dev_id_bytes()` chooses a 2-byte or 4-byte array item size and raises `DevIdBytesTooSmall` when the ID space is exhausted. `network_order_array()` mutates an array into network byte order for serialization and restores the original byte order on exit.

`tiers_for_dev()` and `build_tier_tree()` translate device dictionaries into Swift placement tiers: region, region/zone, region/zone/IP, and region/zone/IP/device-id. The returned tree is a `defaultdict(set)` keyed by parent tier and rooted at `()`. `format_device()`, `pretty_dev()`, and `get_tier_name()` convert tier/device data back into ring-builder display strings.

Address validation is split into `validate_and_normalize_ip()`, `validate_and_normalize_address()`, `is_valid_hostname()`, and `is_local_device()`. IP values are lower-cased and IPv6 addresses are expanded through `swift.common.utils.expand_ipv6`; hostnames are lower-cased and checked against an RFC1123-style label regex. `is_local_device()` may resolve hostnames with `socket.getaddrinfo()` and compares candidate IPs with the local IP set and optional server-per-port port matching.

Ring-builder CLI parsing is handled by `parse_search_value()`, `parse_search_values_from_opts()`, `parse_change_values_from_opts()`, `parse_add_value()`, `parse_address()`, `validate_args()`, `parse_args()`, `parse_builder_ring_filename_args()`, and `build_dev_from_opts()`. These functions parse compact legacy device strings such as `r1z2-10.1.2.3:6200/sdb1_meta`, newer option-parser fields, replication addresses, IPv6 bracket notation, weight, metadata, and change options. `validate_device_name()` rejects empty names and leading/trailing spaces.

`dispersion_report()` reads a builder dispersion graph and max-replica-by-tier model to calculate at-risk partitions and the worst tier. `validate_replicas_by_tier()` checks that a replicas-by-tier map sums back to the expected replica count for cluster, region, zone, server, and device tier depths.

## Control flow

The parsing functions all follow deterministic left-to-right token consumption. `parse_search_value()` peels optional `d`, `r`, and `z` numeric prefixes, optional IP and port, optional replication address after `R`, optional device name after `/`, and optional metadata after `_`; any unconsumed suffix raises `ValueError`. `parse_add_value()` is stricter: zone, primary address, port, and device are required, while region and replication address are optional. `parse_address()` handles bracketed IPv6 by removing a single bracket pair, scans until `R` or `/`, splits at the final colon, validates the port, and normalizes the IP.

Ring tier building is additive: each device contributes every tier from `tiers_for_dev()`, and `build_tier_tree()` records child tiers under each parent. Dispersion reporting refreshes the builder's dispersion graph when requested, skips tiers not matching a search regex, computes excess colocated replica counts above the allowed tier maximum, and optionally accumulates verbose per-tier graph data.

## State and persistence behavior

The module itself has no durable state. Its stateful behavior is limited to in-place byte swapping in `network_order_array()` and array resizing in `resize_array()`. The context manager intentionally mutates the supplied array rather than copying it, so the `finally` block is essential to avoid leaving live ring data in network order on little-endian systems. Ring-builder option parsing returns plain dictionaries that callers persist in builder files elsewhere.

## Dependencies and integration points

The module depends on `swift.common.exceptions` for ring-specific errors and on `swift.common.utils` IP helpers. It imports `optparse` because Swift ring-builder CLI compatibility predates `argparse`. Device dictionaries are expected to use the conventional ring keys `id`, `region`, `zone`, `ip`, `port`, `replication_ip`, `replication_port`, `device`, `weight`, and `meta`. `dispersion_report()` depends on private builder methods and fields (`_dispersion_graph`, `_build_dispersion_graph()`, `_build_max_replicas_by_tier()`, and `devs`), so builder internals and this utility must evolve together.

## Risks and edge cases

The compact parser is intentionally permissive in some places and strict in others. It recognizes IP literals, not hostnames, inside compact search/add strings, while option-based parsing accepts hostnames through `validate_and_normalize_address()`. Empty numeric prefixes such as `d` or malformed port suffixes can surface as `ValueError` from `int()`. IPv6 support depends on bracket handling and final-colon port splitting; tests should cover unbracketed IPv6 rejection for add values and normalized bracketed values.

`is_local_device()` performs DNS resolution for hostnames and returns false on `gaierror`; this avoids startup failures but may mask transient DNS problems. `calc_dev_id_bytes()` reserves the maximum value as the unassigned sentinel, so exact boundary tests around `none_dev_id(2)` and `none_dev_id(4)` are important. `network_order_array()` has mutation risk if callers retain references while serializing.

## Test signals

Useful tests include byte-order round trips, sentinel preservation across `resize_array()`, compact parser examples from the docstring, invalid add/search strings, hostname and IPv6 normalization, device-name validation, server-per-port matching when `my_port` is `None`, and dispersion calculations with a fake builder graph. The strongest integration signal is ring-builder CLI behavior: adding, searching, changing, and displaying devices should remain stable across legacy compact syntax and newer option syntax.
