# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_3gx.yaml

## Purpose
Aggregated large-filesystem fixture for `RP_3GX`, used to validate estimator behavior for three-way replicated data at scale. It shares the same bucketed filesystem summary as the big SX and EC fixtures.

## Important APIs, types, and functions
- Uses the standard estimator YAML hierarchy under `containers`.
- `file_dkey0` and every data/remainder dkey count are tripled compared with SX, reflecting three replicas.
- Directory object counts and superblock metadata are unchanged from other big fixtures.
- Representative objects encode file-size buckets rather than individual files.

## Control flow
The estimator reads this file and recursively applies counts. Replication is represented directly in YAML counts: for example full-data dkeys for 8 MiB, 500 GiB, and 10 TiB files are 3x the SX counts.

## State and persistence behavior
The file has no mutable state. It approximates VOS persistence for a large DFS namespace: one container, repeated directory objects, and repeated file data objects. Since data values are arrays with 128 KiB records, NVMe/SCM attribution depends on `scm_cutoff` during estimator execution.

## Dependencies and integration points
The fixture integrates with storage estimator tests that validate CSV/average generation for `RP_3GX`. It depends on the PyYAML anchor mechanism and on `vos_size.py` treating `overhead` and `value_type` fields consistently.

## Risks and edge cases
Large replicated counts can overflow assumptions in downstream code if totals are held in narrow types outside Python. The fixture’s aggregate nature means a change in average file-size bucketing or replication math requires coordinated updates across all big fixtures.

## Test signals
Signals include parseability, stable totals under `read_yaml`, and expected 3x-style expansion of file data dkey counts relative to the SX big fixture while namespace metadata remains comparable.
