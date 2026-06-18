# sources/object-store/daos/src/vos/storage_estimator/common/tests/test_files/test_data_16p2gx.yaml

## Purpose
Fixture YAML for the storage estimator's detailed DFS sample when regular file data uses `EC_16P2GX`. It models a small POSIX-like tree with two directories, four regular files, one symlink, and DFS superblock metadata, using the VOS estimator schema consumed by `MetaOverhead`.

## Important APIs, types, and functions
- Top-level `num_shards: 1000` drives how many VOS pools/targets the estimator distributes dkeys across.
- YAML anchors define reusable VOS records: DFS superblock akeys, `dfs_inode`, directory dkeys, file dkeys, and per-file object definitions.
- Keys use `type: hashed` for named DFS metadata/directory entries and `type: integer` for file layout dkeys/akeys.
- Akeys declare `value_type: single_value` for inode-like scalar metadata and `value_type: array` for file/symlink data extents.

## Control flow
There is no executable control flow. When loaded by `read_yaml`, `Common._process_yaml` passes the parsed `containers` list to `MetaOverhead.load_container`. The estimator then walks container -> object -> dkey -> akey -> values, with counts multiplying tree and record overhead. The EC fixture differs from the SX/RP variants by inflating per-file integer dkey counts according to EC 16+2 data/parity layout rather than raw logical chunk counts.

## State and persistence behavior
The file is declarative and persists no runtime state. Its state model mirrors DFS/VOS persistence: one container contains superblock metadata, directory objects contain filename dkeys with `DFS_INODE` values, and regular file objects contain metadata dkeys plus array extents at 128 KiB I/O size. `overhead: meta` assigns key/value bytes to metadata, while `overhead: user` attributes named directory/file bytes to user metadata.

## Dependencies and integration points
It depends on the estimator schema implemented by `vos_size.py` and object builders in `vos_structures.py`: required keys include `containers`, `objects`, `dkeys`, `akeys`, `values`, `value_type`, and `size` for hashed keys/values. The fixture is used by storage-estimator tests comparing generated DFS exploration/CSV output for `EC_16P2GX` against known YAML.

## Risks and edge cases
Because anchors are reused heavily, a changed anchor affects many object sections. Counts encode EC placement assumptions; changes to chunk size, I/O size, EC cell handling, or DAOS object class semantics require coordinated fixture updates. The sample contains the historical spelling `very_importan_file.txt`, so tests relying on exact key sizes should preserve it.

## Test signals
Useful signals are successful YAML parsing, stable estimator totals for the EC_16P2GX object class, and expected differences from SX/RP fixtures in integer dkey counts for data extents and parity-influenced layout.
