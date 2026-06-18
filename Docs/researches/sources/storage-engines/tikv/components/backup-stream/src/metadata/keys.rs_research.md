# sources/storage-engines/tikv/components/backup-stream/src/metadata/keys.rs

## Purpose
`metadata/keys.rs` defines the byte key layout for backup stream metadata under `/tidb/br-stream` and provides helpers for constructing, comparing, debugging, and decoding those keys.

## Important APIs, types, and functions
- `MetaKey(Vec<u8>)` is the typed key wrapper; `KeyValue(MetaKey, Vec<u8>)` is the metadata key-value pair.
- Key families include `/info`, `/checkpoint`, `/storage-checkpoint`, `/ranges`, `/pause`, and `/last-error`.
- Constructors include `tasks`, `task_of`, `ranges_of`, `range_of`, `next_backup_ts`, `next_backup_ts_of`, `next_bakcup_ts_of_region`, `storage_checkpoint_of`, `pause_prefix`, `pause_of`, `last_errors_of`, `last_error_of`, and `central_global_checkpoint_of`.
- `next` and `next_prefix` construct exclusive range ends for exact-key and prefix reads.
- `extract_name_from_info` and `extrace_name_from_pause` decode task names from watch keys.

## Control flow
Callers use constructors to create keys, then `Keys::into_bound` in `store/mod.rs` converts them to range bounds. Range records encode the task start key after the ranges prefix and store the end key as the value; `KeyValue::take_range` reverses that encoding.

## State and persistence behavior
This file defines the persistent path contract. Task info and error values are protobuf bytes, checkpoint/storage checkpoint values are big-endian `u64`s, pause values are empty or JSON, and ranges use binary suffix/value pairs.

## Dependencies and integration points
It depends on `kvproto::metapb::Region` for region checkpoint key generation and `tikv_util::codec::next_prefix_of` for prefix bounds. Every metadata client and store adapter depends on this layout.

## Risks and edge cases
- Task names are interpolated directly into path strings, so path separator handling depends on upstream task-name constraints.
- Region/store ids are encoded as decimal path segments despite comments mentioning big-endian ids in the older design note.
- The typo `extrace_name_from_pause` and `next_bakcup_ts_of_region` should be preserved unless all callers are migrated.
- Empty region end keys and arbitrary binary range start keys make range-prefix slicing sensitive to exact prefix length.

## Test signals
`metadata/test.rs::test_storage_checkpoint_of` asserts the storage checkpoint path. `metadata/client.rs::test_parse` verifies checkpoint paths generated here can be parsed back into `Checkpoint` values.
