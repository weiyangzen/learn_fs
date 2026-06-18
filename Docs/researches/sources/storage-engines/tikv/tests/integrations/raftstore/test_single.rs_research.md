<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_single.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_single.rs

## Purpose
This file tests basic single-region/single-node raftstore commands across node/server and v1/v2 cluster variants: put, delete, delete range, wrong store ID rejection, large entry rejection, and initial no-op apply.

## Important APIs, Types, and Functions
Tests use `new_put_cmd`, `new_request`, `batch_put`, `must_delete`, `test_delete_range`, `call_command_on_node`, `ReadableSize`, `RAFT_INIT_LOG_INDEX`, random data selection, and `#[test_case]` to run against multiple cluster constructors.

## Control Flow and Behavior
`test_put` writes 999 keys in batches, samples random keys, overwrites all values, and samples again. `test_delete` writes batches and deletes sampled keys. Delete-range tests toggle `use_delete_range` and exercise default/write CF cleanup. `test_wrong_store_id` mutates the request header peer store ID and expects a non-empty error. `test_put_large_entry` sets `raft_entry_max_size` and expects `raft_entry_too_large`. `test_node_apply_no_op` waits until applied index advances beyond `RAFT_INIT_LOG_INDEX`.

## State and Persistence
The tests validate values read through the cluster API and delete-range effects in underlying CFs. The no-op test directly checks apply state progress.

## Dependencies and Integration Points
The file is a low-level integration smoke suite for raftstore request building, command validation, storage CF deletion, size checks, and apply-worker progress. It covers both legacy and v2 cluster constructors where supported.

## Risks
Regressions include batched puts not applying atomically, overwrites not replacing values, delete range leaving CF data behind, request peer validation accepting wrong store IDs, oversize entries entering raft, or a bootstrapped node failing to apply the no-op log.

## Test Signals
Signals are sampled value equality, deleted keys returning `None`, non-empty command error for wrong store ID, `has_raft_entry_too_large`, and applied index exceeding `RAFT_INIT_LOG_INDEX` within the timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_single.rs -->
