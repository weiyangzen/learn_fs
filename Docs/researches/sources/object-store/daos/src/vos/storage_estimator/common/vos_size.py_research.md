# sources/object-store/daos/src/vos/storage_estimator/common/vos_size.py

## Purpose
Core VOS metadata overhead calculator. It converts estimator YAML into per-pool tree structures and accumulates metadata, user metadata, user values, SCM, and NVMe totals using VOS metadata-size definitions.

## Important APIs, types, and functions
- `convert()` and `print_total()` format byte counts.
- `check_key_type()` validates hashed/integer key specs and requires `size` for hashed keys.
- `Stats` stores counters for pool, container, object, dkey, akey, arrays, single values, user bytes, and physical totals.
- `MetaOverhead` builds internal pool/container/object/dkey/akey/value trees and calculates overhead with `init_container`, `init_object`, `init_dkeys`, `init_akey`, `init_value`, `calc_tree`, and `print_report`.

## Control flow
`MetaOverhead` starts with one logical tree per pool. Loading a container appends a container tree to every pool, then each object distributes dkeys across selected targets. Values update akey value/meta/NVMe counters. Reporting adds fixed pool/container roots, recursively computes B-tree overhead based on metadata YAML tree orders, applies duplication counts, and prints a breakdown.

## State and persistence behavior
State is in-memory only: pool trees, next object/container ids, SCM cutoff, checksum size, and accumulated stats. Values above `_scm_cutoff` contribute to `nvme_size`; value bytes still count in logical `total`. Checksum overhead is added per value, with arrays scaled by `ceil(size / csum_gran)`.

## Dependencies and integration points
Consumes metadata from `VOS_SIZE.get_vos_size_str()` or a user-supplied metadata YAML. Used by `Common._process_yaml` for all estimator modes. It depends on tree metadata fields such as `record_msize`, `order`, `leaf_node_size`, `int_node_size`, `num_dynamic`, and `dynamic`.

## Risks and edge cases
Dkey distribution uses `random.randint`, so per-pool layout can be nondeterministic, though aggregate totals should usually remain stable. `get_dynamic` raises a string on impossible state, which is invalid in modern Python. `Stats.merge` assumes every key exists in the child. Dynamic tree sizing is approximate for large counts and assumes 50 percent capacity when values exceed order.

## Test signals
Signals include validation errors for malformed YAML, stable aggregate totals for fixtures, correct SCM/NVMe split around cutoff, checksum overhead scaling, and sensible metadata growth as dkey/akey/value counts increase.
