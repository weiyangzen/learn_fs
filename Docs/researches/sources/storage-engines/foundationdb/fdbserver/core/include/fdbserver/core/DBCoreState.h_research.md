# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DBCoreState.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DBCoreState.h

Purpose: defines the persistent core database state stored in coordinated state, including current and old transaction log topologies, recovery count, protocol versions, pseudo-localities, and backup tag counts.

Important APIs/types: `CoreTLogSet`, `OldTLogCoreData`, and `DBCoreState`; methods `CoreTLogSet::operator==`, serializers, `OldTLogCoreData::operator==`, `DBCoreState::getPriorCommittedLogServers`, `isEqual`, and serialization.

Control flow and state: `CoreTLogSet` records log server UIDs, write anti-quorum, replication factor, localities, replication policy, locality role, start version, satellite tag locations, and TLog version. `OldTLogCoreData` records prior log sets and epoch ranges needed for recovery/backup. `DBCoreState` records current log sets, old logs, recovery count, log system type, protocol compatibility, and deprecated encryption field retained for downgrade safety. `getPriorCommittedLogServers` flattens all current and old log server IDs.

State and persistence behavior: comments explicitly mark this as persisted in `CoordinatedState` and version-sensitive. Serialization gates fields on protocol features such as backup worker, GC transaction generations, software version tracking, encryption-at-rest, and range backup worker. Equality optionally includes `recoverAt` depending on `RECORD_RECOVER_AT_IN_CSTATE`.

Dependencies and integration: depends on replication policy, log system config, master interface, server knobs, object serializer traits, and protocol version helpers. Master recovery reads/writes it to define durable transaction log topology.

Risks and tests: adding/removing/reordering fields can break coordinator-persisted state and downgrade paths. Deprecated encryption bytes must remain until a deliberate migration exists. Tests should cover serialization across protocol versions, equality with/without recoverAt knob, recovery with old log data, and downgrade compatibility.
