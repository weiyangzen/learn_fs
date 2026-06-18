# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/AccumulativeChecksum.h

Purpose: defines the serialized state for accumulative checksum tracking.

Important APIs and types: `AccumulativeChecksumState` carries `acsIndex`, checksum value `acs`, `version`, and `epoch`. It has constructors for default invalid state and initialized state, `toString`, `serialize`, and a `file_identifier` for FDB serialization.

State and persistence: this is a persistence contract. Instances can be serialized through `serializer(ar, acsIndex, acs, version, epoch)` and likely stored or transmitted by logging/verification paths. Default state uses checksum `0`, `invalidVersion`, epoch `0`, index `0`.

Dependencies and integration: includes `FDBTypes.h` for `Version` and `fdbrpc.h` for serialization/RPC types such as `LogEpoch`.

Risks: field order is part of the wire/storage compatibility contract. Changing types or serialization order would break compatibility. `toString` is diagnostic only and should not be parsed as stable data.

Test signals: no local tests; correctness is covered where accumulative checksum state is serialized/deserialized and compared in log or recovery flows.
