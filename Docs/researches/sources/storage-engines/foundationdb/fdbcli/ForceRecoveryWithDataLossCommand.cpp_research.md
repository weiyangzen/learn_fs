# sources/storage-engines/foundationdb/fdbcli/ForceRecoveryWithDataLossCommand.cpp

Purpose: Implements `force_recovery_with_data_loss <DCID>`, an emergency command that forces recovery into a specified datacenter and accepts potential committed mutation loss.

Important APIs/types/functions: `forceRecoveryWithDataLossCommandActor(Reference<IDatabase>, tokens)`, `db->forceRecoveryWithDataLoss(tokens[1])`, `safeThreadFutureToFuture`, and `CommandFactory forceRecoveryWithDataLossFactory`.

Control flow: The actor requires exactly two tokens. Invalid usage prints help and returns false. Valid usage forwards the DCID token to the database API and returns true after the future completes. It does not catch errors locally; fdbcli outer handling is expected to report them.

State and persistence behavior: The command delegates all durable behavior to the database management API. Per help text, it changes region configuration priorities, sets `usable_regions` to 1, and does nothing if the database has already recovered. No local state is written.

Dependencies and integration points: Depends on multiversion database interface support for force recovery and fdbcli command registration. Operationally tied to multi-region disaster recovery configuration.

Risks: Data-loss inducing by design. There is no interactive confirmation in this file; any confirmation must be enforced by higher-level command dispatch if desired. Validation of the DCID and recovery conditions is delegated to the database API.

Test signals: Cover token-count validation, successful delegation, propagated API errors, already-recovered no-op behavior at integration level, and documentation/confirmation expectations in the command dispatcher.
