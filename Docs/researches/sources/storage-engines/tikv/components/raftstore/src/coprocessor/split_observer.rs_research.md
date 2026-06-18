# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_observer.rs

Purpose: Implements the raftstore admin coprocessor that sanitizes Split and BatchSplit requests before proposal. Its main job is to strip MVCC timestamps from split keys, reject empty/out-of-region keys, deduplicate adjacent versions of the same logical key, and keep split requests sorted so a split does not separate multiple MVCC versions of one user key.

Important APIs and types: `NO_VALID_SPLIT_KEY` is the user-visible failure text when every requested split point is discarded. `strip_timestamp_if_exists` attempts `tikv_util::codec::bytes::decode_bytes` and truncates the undecoded suffix, treating it as a timestamp when the key was encoded. `is_valid_split_key` rejects empty keys and uses `store::util::check_key_in_region_exclusive` to reject region edges or outside keys. `SplitObserver` implements `Coprocessor` and `AdminObserver`; `pre_propose_admin` is the integration point invoked before proposing admin commands.

Control flow: `pre_propose_admin` only handles `AdminCmdType::Split` and `AdminCmdType::BatchSplit`. It validates that the matching request payload exists, moves the split requests out of the protobuf, calls `on_split`, and writes back the cleaned request list. `on_split` consumes the split vector, strips timestamps, filters invalid keys, then uses `itertools::coalesce` to keep strictly increasing split keys and drop duplicates or unsorted keys. If no valid split remains, it returns `NO_VALID_SPLIT_KEY`.

State and persistence: This file has no durable state. It mutates only the in-flight `AdminRequest` before raft proposal. The important persistence implication is indirect: by normalizing split keys before proposal, the persisted region boundary will be a user-key boundary instead of a versioned MVCC key boundary.

Dependencies and integration points: It depends on protobuf request types from `kvproto::raft_cmdpb`, region metadata from `kvproto::metapb`, TiKV byte encoding helpers, and raftstore region range validation. It integrates with the coprocessor framework through `AdminObserver::pre_propose_admin` and surfaces errors through the coprocessor `Result`.

Risks: The timestamp stripping heuristic treats raw keys that happen to decode as encoded keys as encoded keys, which the comment calls out as intentional but subtle. Invalid split requests with all keys filtered fail the proposal; mixed valid/invalid requests silently drop invalid keys after logging. Ordering is strict; out-of-order split keys are dropped rather than sorted into the requested order.

Test signals: `test_forget_encode` verifies timestamp stripping from encoded row keys. `test_split` covers non-split commands, single split compatibility, empty/start keys, duplicate MVCC versions, row/index/table-prefix keys, raw keys, right-derive preservation, and the all-invalid error path.
