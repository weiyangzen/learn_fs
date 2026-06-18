# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_big_16p2gx.yaml

## Purpose
Aggregated large-filesystem fixture for the storage estimator using `EC_16P2GX`. Instead of enumerating each directory and file, it summarizes a large DFS population into object buckets for directories, symlinks, and representative file-size classes.

## Important APIs, types, and functions
- Header comments record source aggregate counts: total objects, total size, directory count, link count, and file buckets for 4 KiB, 256 KiB, 8 MiB, 500 GiB, and 10 TiB.
- `dir_obj` uses `count: 4931` and average dkeys for symlinks, subdirectories, and files per directory.
- Representative file objects (`4k_obj`, `256k_obj`, `8m_obj`, `500g_obj`, `10t_obj`) multiply by file count.
- EC-specific counts model full 1 MiB dkeys plus parity/remainder dkeys; large objects include comments showing EC count formulas for 500 GiB and 10 TiB.

## Control flow
The fixture is consumed as ordinary YAML. `MetaOverhead` multiplies each representative object by its `count`, then each dkey/akey/value by its local counts. The file buckets are therefore an averaged approximation of a huge filesystem, not an exact per-file listing.

## State and persistence behavior
No runtime state is stored. The model persists aggregate VOS shape: one superblock, many similar directory objects, and file data represented by repeated full-chunk dkeys plus remainder dkeys. `csum_size: 0` means checksum overhead is disabled in this fixture.

## Dependencies and integration points
This file supports tests of the estimator's `-x` average/massive-filesystem path and CSV-to-YAML logic. It depends on the same schema as the detailed fixtures and on object-class accounting used by `ProcessCSV`/DFS exploration when EC_16P2GX is selected.

## Risks and edge cases
The bucketed model hides variance inside each class; it is useful for totals but not for exact tree topology. Very large dkey counts stress dynamic tree-order calculations in `MetaOverhead.get_dynamic`; stale counts can produce large total differences. Object names beginning with digits are valid YAML anchors here but may be awkward for manual tools.

## Test signals
Expected signals are successful parse, stable aggregate totals, correct handling of millions of repeated dkeys, and EC totals that are larger than SX but not simply 3x like RP_3GX.
