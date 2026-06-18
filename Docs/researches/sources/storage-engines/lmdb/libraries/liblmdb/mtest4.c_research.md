# sources/storage-engines/lmdb/libraries/liblmdb/mtest4.c

## Purpose
`mtest4.c` targets sorted duplicate databases with fixed-size duplicate data, especially duplicate page split paths and `MDB_NEXT_MULTIPLE`.

## Important APIs, types, and functions
The program opens subDB `"id4"` with `MDB_CREATE|MDB_DUPSORT|MDB_DUPFIXED`, inserts fixed-size duplicate values with `MDB_NODUPDATA`, uses aborting transactions to exercise split branches, and reads batches with `MDB_NEXT_MULTIPLE`.

## Control flow
It creates 510 deterministic duplicate values under key `"001"`, which should fill at least one duplicate page. It then tries insertions near the lower half, split point, and upper half of the duplicate set, aborting two and committing one to hit different split code paths. It scans duplicate groups with `MDB_NEXT_MULTIPLE`, deletes a random stride of values, and performs final forward/backward cursor scans.

## State and persistence behavior
The test persists one duplicate-heavy subDB in `./testdb` under `MDB_FIXEDMAP|MDB_NOSYNC`. Aborted insert transactions should leave no state; the committed upper-half insertion should persist.

## Dependencies and integration points
It directly exercises duplicate fixed-size leaf layout, duplicate subpage splitting, and multiple-value cursor retrieval in LMDB internals.

## Risks and edge cases
Deletion stride uses `rand()%3`, which can be zero. Fixed-size buffers and `sizeof(int)` key sizing assume the literal key representation fits. The test is sensitive to page size and duplicate-page thresholds.

## Test signals
Expected output includes successful full duplicate scan, no errors from split-path insertions, `MDB_NEXT_MULTIPLE` returning packed duplicate data, and correct final traversal after deletes.
