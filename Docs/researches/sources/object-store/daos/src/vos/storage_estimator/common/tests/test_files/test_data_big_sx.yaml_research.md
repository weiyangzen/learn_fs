# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_sx.yaml

## Purpose
Baseline aggregated large-filesystem fixture for `SX` spreading. It provides the non-replicated, non-EC reference for the big filesystem model used by estimator tests.

## Important APIs, types, and functions
- Header comments define the source aggregate dataset and bucket counts.
- Directory population is represented through `dir_obj count: 4931` with average symlink, subdirectory, and file dkeys.
- File objects represent size classes and use full 1 MiB data dkeys plus remainder dkeys.
- `containers: [*posix]` is the only top-level executable input for `MetaOverhead`.

## Control flow
Loaded YAML is walked by the estimator. Counts multiply through the tree: container count, object count, dkey count, akey count, and value count. `SX` baseline counts encode logical data once, so other object-class fixtures can be compared against it.

## State and persistence behavior
The file encodes static aggregate VOS state: DFS superblock metadata, repeated directory inode records, symlink arrays, and representative file arrays. It disables checksums with `csum_size: 0`.

## Dependencies and integration points
It is a reference input for storage-estimator average mode and for validating `ProcessCSV`/filesystem exploration output. It depends on `MetaOverhead` dynamic tree sizing to scale metadata records for huge dkey counts.

## Risks and edge cases
Because this is the baseline, errors here propagate into expectations for replicated and EC comparisons. Counts are averages and ceilings, so they should not be used as proof of exact per-directory layout. Huge counts exercise estimator performance and integer arithmetic.

## Test signals
Expected signals are stable baseline totals, successful handling of large dkey counts, and lower data/storage totals than RP_3GX or EC_16P2GX variants.
