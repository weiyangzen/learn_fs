# sources/object-store/openstack-swift/swift/account/replicator.py

## Purpose
Defines the account replicator daemon by specializing Swift's common database replicator for account databases.

## Important APIs, Types, and Functions
`AccountReplicator` extends `db_replicator.Replicator` and sets `server_type = 'account'`, `brokerclass = AccountBroker`, `datadir = DATADIR`, and `default_port = 6202`. `main()` adds `--devices` and `--partitions` options for one-shot scoped replication, parses options, and runs the daemon.

## Control Flow
The common replicator framework handles scanning devices/partitions, comparing DB states, rsync/HTTP replication, and cleanup. This subclass supplies the account-specific broker, datadir, and default port.

## State and Persistence Behavior
Persistent state is account SQLite DBs under the `accounts` datadir and replication metadata such as sync points in DB tables. The replicator converges account DBs across nodes and eventually reclaims tombstoned DBs.

## Dependencies and Integration Points
Depends on `AccountBroker`, `DATADIR`, `swift.common.db_replicator`, `run_daemon`, and `parse_options`. It integrates with account-server config `[account-replicator]`, rsync modules, rings, and broker merge logic.

## Risks and Test Signals
Most risk is inherited from common DB replication: stale sync points, rsync config mismatch, broker migration compatibility, and scoped `--devices`/`--partitions` only applying in once mode. Test signal is account DB convergence across replicas and correct handling of scoped one-shot replication.
