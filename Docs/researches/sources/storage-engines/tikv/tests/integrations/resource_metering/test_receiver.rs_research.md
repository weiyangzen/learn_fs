# sources/storage-engines/tikv/tests/integrations/resource_metering/test_receiver.rs

Purpose: tests single-target receiver reporting behavior under address changes, receiver blocking, and shutdown.

Important APIs and functions: `TestSuite::start_receiver_at`, `shutdown_receiver`, `block_receiver`, `unblock_receiver`, `cfg_receiver_address`, `setup_workload`, `cancel_workload`, `flush_receiver`, `block_receive_one`, and `nonblock_receiver_all`.

Control flow: `test_alter_receiver_address` confirms records with a valid receiver, silence on an invalid port, and resumed records after restoring the address. `test_receiver_blocking` blocks the mock receiver handler and expects no records until unblocked. `test_receiver_shutdown` changes workload tags, shuts down the receiver, flushes, and expects no further records.

State and persistence: reporter connection state, mock receiver lifecycle, atomic block flag, and received-record channel are the main state. Temporary storage only creates workload.

Dependencies and integration: resource metering single-target reporter, dynamic receiver config, client-streaming gRPC receiver, and shared mock receiver.

Risks: sleep-based timing and blocked RPC behavior can be flaky; a blocked receiver can create reporter backpressure.

Test signals: proves reports follow live receiver address state and are suppressed while the receiver is unavailable or blocked.
