# sources/storage-engines/foundationdb/fdbcli/DataDistributionCommand.cpp

Purpose: Implements hidden `datadistribution` controls for enabling/disabling all data distribution or selected data-distribution subfunctions such as storage-server failure handling and rebalance modes.

Important APIs/types/functions: `dataDistributionCommandActor`, `setDDMode`, `setDDIgnoreRebalanceSwitch`, `setDDIgnoreRebalanceOn`, `setDDIgnoreRebalanceOff`, special keys `ddModeSpecialKey` and `ddIgnoreRebalanceSpecialKey`, `rebalanceDDIgnoreKey`, `DDIgnore` masks, plus maintenance helpers `setHealthyZone` and `clearHealthyZone`.

Control flow: The actor accepts `on`, `off`, `disable <ssfailure|rebalance|rebalance_disk|rebalance_read>`, and matching `enable` forms. `setDDMode` writes the mode special key and, when enabling, clears global storage-failure maintenance state and rebalance-ignore state. Rebalance switches read the old mask, treating empty legacy values as `DDIgnore::ALL`, set or clear the masked bits, and remove the key when the mask becomes zero. Storage-server failure disable is implemented through maintenance state with `IgnoreSSFailures`; enable clears that state.

State and persistence behavior: Persists cluster-wide management special keys under `\xff\xff/management/data_distribution/...` and maintenance keys. The hidden command modifies live DD behavior and can leave the cluster unable to rebalance or react to failures until re-enabled.

Dependencies and integration points: Integrates with maintenance command state, DD ignore masks, special key space, `CLIENT_KNOBS->TOO_MANY`, Flow retry loops, and status warnings that surface DD disabled states.

Risks: High operational blast radius. Legacy empty-value handling must remain correct during upgrades. `tokens[2]` is used in the `disable/enable` branches after a broad size check that permits size 2; if a user enters only `datadistribution disable`, this can index past the token vector. Tests should catch this parser hazard.

Test signals: Cover `on/off`, each disable/enable submode, legacy empty mask upgrade, clearing DD side effects, invalid argument handling including missing third token, and status JSON warnings.
