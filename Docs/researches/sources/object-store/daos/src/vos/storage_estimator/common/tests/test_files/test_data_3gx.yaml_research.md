# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_3gx.yaml

## Purpose
Fixture YAML for the same detailed DFS sample as the SX and EC files, but with regular file data modeled for `RP_3GX` three-way replicated placement. It lets tests verify that replicated object classes expand dkey/value counts differently from spreading or erasure coding.

## Important APIs, types, and functions
- Uses the same estimator schema and anchors as `test_data_sx.yaml`.
- `num_shards: 1000` gives the placement simulator a large target set.
- File metadata dkeys and remainder/data dkeys are integer-keyed, with replicated counts such as larger `driver_dkey1`, `secret_plan_dkey1`, and `very_important_dkey1`.
- DFS metadata and directory records remain hashed and mostly identical across object classes.

## Control flow
The file is read by PyYAML, then `MetaOverhead` recursively initializes objects and distributes dkeys across target pools. Replication is pre-modeled by larger dkey counts in the fixture rather than by runtime object-class parsing in `read_yaml`.

## State and persistence behavior
The persisted model is a single DFS container with one superblock object, directory entry objects, symlink data, and four file data objects. Counts represent repeated VOS records for replicated data: metadata dkeys for file inodes are tripled, and array dkey counts scale to three copies.

## Dependencies and integration points
It integrates with storage-estimator test cases that compare an explored/generated filesystem model against static YAML for `RP_3GX`. It relies on `check_key_type` accepting `hashed` and `integer`, and on estimator checksum defaults (`csum_size: 0`, `csum_gran: 16384`).

## Risks and edge cases
The fixture can silently become stale if the replication/object-class accounting changes. It also depends on exact UTF-8 byte lengths in `size` fields for file names and DFS keys. Because replicated count changes are local to selected integer dkeys, tests should compare structure, not only total bytes, when debugging failures.

## Test signals
Expected signals include parseability, stable metadata/user/NVMe totals for a three-way replicated layout, and larger data dkey counts than the SX fixture while preserving identical directory and DFS superblock sections.
