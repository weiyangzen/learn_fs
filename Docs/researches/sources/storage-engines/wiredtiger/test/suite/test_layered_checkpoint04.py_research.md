# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint04.py

Purpose: verifies that a leader can create a disaggregated checkpoint solely to publish a stable timestamp update, even with no dirty table data, and that followers cannot publish such checkpoints themselves.

Important APIs/types/functions: `test_layered_checkpoint04` uses `disagg_test_class`, `gen_disagg_storages`, `make_scenarios`, `wiredtiger_open`, `disagg_get_complete_checkpoint_ext`, `disagg_get_complete_checkpoint_meta`, `disagg_advance_checkpoint`, `query_timestamp('get=last_checkpoint')`, and stdout pattern matching.

Control flow: the test creates a layered table, opens a follower, writes timestamp 10 data, checkpoints, verifies complete checkpoint timestamp 10, advances the follower, and checks follower last checkpoint. It then advances only the leader stable timestamp to 20 and checkpoints without dirtying data. It verifies the complete checkpoint timestamp changed to 20 and the follower picks it up. Next, it writes on the follower and checkpoints there at timestamp 30, then verifies the shared complete checkpoint remains timestamp 20. Finally, it advances the same checkpoint again and checks idempotent log output plus unchanged metadata LSN.

State and persistence behavior: tracks leader stable timestamp, follower last checkpoint timestamp, complete checkpoint metadata, and metadata LSN. Follower-local writes must not mutate shared checkpoint state.

Dependencies/integration points: exercises disaggregated leader/follower role semantics, checkpoint metadata publication, timestamp query APIs, and checkpoint pickup idempotence.

Risks: false positives are limited because timestamp and metadata LSN assertions are explicit. A subtle risk is the test assumes the expected stdout message for repeated pickup remains stable.

Test signals: passing proves timestamp-only leader checkpoints are durable/pickup-visible, follower checkpoints are local-only for shared metadata, and duplicate pickup leaves shared metadata unchanged.
