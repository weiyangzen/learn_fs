# sources/storage-engines/tikv/tests/integrations/raftstore/test_lease_read.rs

Purpose: exhaustive lease-read and read-index correctness suite for raft leaders. It covers lease renewal by reads/writes, expired leases, transfer-leader unsafe periods, batch snapshot lease IDs, callback cleanup on destroyed regions, stale read-index protection, local read cache, leadership changes during read-index, automatic lease renewal, continuous local-read renewal, and restart during isolation.

Important APIs and functions: `test_renew_lease!` is the main shared scenario. Tests use `configure_for_lease_read`, `LeaseReadFilter`, `must_read_on_peer`, `must_error_read_on_peer`, `async_read_on_peer`, `batch_read_on_peer`, `make_cb_rocks`, `new_read_index_cmd`, raft message filters, `LeadingFilter`, and PD peer changes. `assert_le!` bounds read-index renewals during continuous reads.

Control flow: scenarios configure long or short election/lease intervals, force a peer to lead, issue local reads while the lease is valid, wait for expiration to require read-index, perform writes to renew lease, and install filters to simulate transfer, isolation, delayed heartbeat responses, or destroyed regions. Several tests use explicit channels/callbacks to observe pending read-index completion.

State and persistence: observed state includes raft local last index, apply index, read-index values, shared `RocksSnapshot` pointers for batched reads, engine key data, leader cache, peer replacement state, and error headers such as stale command or region not found.

Dependencies and integration points: integrates raft leader lease logic, local reader cache, read-index batching, raft transfer-leader flow, PD membership, callbacks, snapshot batching, raftstore v1/v2 cluster variants, and timing configuration.

Risks: extremely timing-sensitive; sleeps model lease expiration, election timeout, heartbeat intervals, and renewal ticks. Some tests are disabled for raftstore-v2 where batch get snapshot is unsupported. Correctness hinges on not batching read-index requests across writes or suspect-lease boundaries.

Test signals: local reads do not increase raft index under valid lease, expired or unsafe leases trigger read-index, callbacks finish with errors rather than deadlocking when regions are destroyed, stale read-index returns stale-command errors, read-index after write is at least applied index, and isolated old leaders cannot serve stale lease reads after restart/election.
