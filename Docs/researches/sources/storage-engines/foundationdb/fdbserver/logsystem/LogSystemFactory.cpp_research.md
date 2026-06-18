# sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemFactory.cpp

Purpose: Provides small factory wrappers that decouple callers from direct `LogSystem` and `LogSystemConsumer` construction and from the concrete tag-partitioned implementation selection.

Important APIs/types/functions: `recoverAndEndLogSystemEpoch`, `makeLogSystemFromLogSystemConfig`, `makeOldLogSystemFromLogSystemConfig`, `makeLogSystemFromServerDBInfo`, and `makeLogSystemConsumerFromServerDBInfo`.

Control flow: `recoverAndEndLogSystemEpoch` forwards to `LogSystem::recoverAndEndEpoch`. The config factories return an empty reference for `LogSystemType::empty`, call `LogSystem::fromLogSystemConfig` or `LogSystem::fromOldLogSystemConfig` for `LogSystemType::tagPartitioned`, and throw `internal_error` for unknown types. Server DB info helpers extract locality and log-system config from `ServerDBInfo`, create a `LogSystem`, and optionally wrap it in a consumer.

State and persistence behavior: No state is owned or persisted here. The functions instantiate references based on already-persisted log-system config and pass through `useRecoveredAt`, `excludeRemote`, and optional actor collection parameters that affect the constructed `LogSystem`.

Dependencies and integration points: Depends on `LogSystemFactory.h`, `LogSystem.h`, `LogSystemConsumer.h`, `DBCoreState`, `ServerDBInfo`, `LogSystemConfig`, and Flow actor futures. This is the narrow integration point for components that need a log system but should not branch on log-system type themselves.

Risks: Only `empty` and `tagPartitioned` are recognized; adding another `LogSystemType` requires updating this factory or callers will hit `internal_error`. Returning null for empty configs requires callers to handle absence. The wrapper preserves `excludeRemote` and `useRecoveredAt` semantics, so incorrect caller flags can construct a log-system view with missing remote logs or different recovery end behavior.

Test signals: Build/link tests are the main direct signal. Unit tests should cover empty config returning null, tag-partitioned config returning a usable `LogSystem`, old-log construction, consumer creation from `ServerDBInfo`, and unknown type failure if a new enum value is introduced without factory support.
