# sources/storage-engines/foundationdb/fdbserver/workloads/CheckMetadataEncoding.cpp

## Purpose
`CheckMetadataEncoding.cpp` defines `CheckMetadataEncodingWorkload`, which validates whether `keyServers` and `serverKeys` metadata use old or shard-encoded formats according to `SERVER_KNOBS->SHARD_ENCODE_LOCATION_METADATA`. It is intended for forward migration and rollback tests of shard-encoded location metadata.

## Important APIs, Types, And Functions
The main type is `CheckMetadataEncodingWorkload : TestWorkload`, registered with `WorkloadFactory`. It uses `keyServersPrefix`, `keyServersEnd`, `serverKeysPrefix`, `serverKeysTrue`, `serverKeysFalse`, `serverKeysTrueEmptyRange`, `BinaryReader`, protocol-version feature detection via `hasShardEncodeLocationMetaData`, and transaction options `READ_SYSTEM_KEYS` and `READ_LOCK_AWARE`.

## Control Flow
Client 0 runs `_start`. It scans all `keyServers` metadata in batches of 1000 and classifies entries as old if values are empty or if the encoded value's protocol version lacks shard-encode support; otherwise they are new. It then scans `serverKeys` entries and classifies known boolean/empty-range values as old and everything else as new. Finally it emits counts and checks them against `shardEncodeExpected` and `allowMixedFormats`.

## State And Persistence
The workload is read-only except for trace output. It observes system metadata state in `keyServers` and `serverKeys`, retrying reads on transaction errors. `setup` can emit an error if `requireKnobFalse` was requested but the server knob is still true.

## Dependencies And Integration Points
This workload depends on FDB system key layout, protocol-version-aware serialization, the shard encoding knob, and rollback scenarios where old and new metadata can intentionally coexist. It integrates with simulation/configuration tests that toggle the feature knob.

## Risks
The serverKeys classification treats any non-legacy sentinel value as new format, so future old-format sentinel additions would need updates. The keyServers check only requires at least one new-format entry when enabled, acknowledging partial migration. In rollback mode, `allowMixedFormats` suppresses errors for leftover new entries; without it, migration residue will fail the test.

## Test Signals
Primary traces are `CheckMetadataEncodingKnobNotFalse`, `CheckMetadataEncodingResult`, and `CheckMetadataEncodingFailed`. The workload returns true from `check`, so error-severity traces and assertions are the test evidence.
