# sources/storage-engines/foundationdb/fdbserver/workloads/DataLossRecovery.cpp

Purpose: Tests recovery behavior after intentional data loss: a shard is manually moved to a single storage server, that process is killed, data distribution is re-enabled with the dead address excluded, and the key is expected to disappear before being writable again.

Important APIs/types/functions: `DataLossRecoveryWorkload`, `disableDDAndMoveShard`, `moveKeys`, `MoveKeysParams`, `MoveKeysLock`, `setDDMode`, `excludeServers`, `checkForExcludingServers`, `getStorageServers`, `GetStorageMetricsRequest`, `getAddressesForKey`, and simulator `killProcess`.

Control flow: Client 0 writes and verifies an initial key, disables DD, chooses a live unprotected storage server, locks and moves the shard to that single server, validates address placement, kills the process, verifies reads time out, enables DD, excludes the failed address, verifies the value is absent, and writes a new value.

State and persistence behavior: The workload mutates one user key and system DD/exclusion/move-keys metadata. It writes `moveKeysLockOwnerKey`, invokes logical or physical data movement depending on knobs, and relies on exclusion to drop unrecoverable shard data. Runtime `pass` is cleared on validation mismatch.

Dependencies/integration: It disables `RandomMoveKeys` and `Attrition`, uses MoveKeys internals, DD mode controls, management exclusions, storage-server metrics RPCs, simulator process state, and system-key transactions.

Risks: This is highly simulation- and timing-sensitive. Selecting a dead server before DD cleanup would hang without the metrics probe. Move-key conflicts and finish retries are expected transient errors. Assertions assume a single-address placement after the move.

Test signals: Phase traces, `TestKeyMoved`, `TestTeamKilled`, `ExcludedFailedServer`, read timeout verification, absent value verification, and final `check()` returning `pass`.
