# sources/storage-engines/foundationdb/fdbclient/DatabaseConfiguration.cpp

## Purpose

`DatabaseConfiguration.cpp` parses, stores, validates, mutates, and serializes FoundationDB database configuration state read from system keys. It covers replication, storage/log engines, proxy/resolver/log counts, remote and satellite regions, backup workers, perpetual storage wiggle, storage migration, exclusions, and conversion between internal key-value form and JSON/configure strings.

## Important APIs, Types, And Functions

`DatabaseConfiguration::resetInternal()` restores derived fields to invalid/default values while intentionally preserving raw configuration storage. Primitive `parse()` helpers convert `ValueRef` text to integers, `int64_t`, doubles, replication policies, and region vectors. Region parsing reads a status JSON object with region/datacenter/satellite data, supports named satellite redundancy modes, fills fallback settings, and sorts by priority.

`setDefaultReplicationPolicy()` constructs default `PolicyAcross(..., "zoneid", PolicyOne)` policies for storage, tLogs, remote tLogs, and satellite tLogs when explicit policies are absent. `maxZoneFailuresTolerated()` computes tolerated zone failures for single-region and HA/georeplicated configurations, accounting for tLog anti-quorum, storage team size, usable regions, and satellite fallback replication.

`isValid()` enforces a large set of invariants: initialized config, positive process counts, supported tLog versions and engines, valid spill/storage settings, proxy auto-counts, replication policies, remote log settings, region cardinality, unique datacenter IDs, satellite validity, perpetual wiggle locality, and storage migration type. `toJSON()` emits a status/configuration object, using named redundancy modes when the current numeric/policy combination matches known modes and falling back to custom replica/policy fields otherwise. `configureStringFromJSON()` converts JSON back into a configure command string, with legacy compatibility for missing `log_engine`.

`setInternal()` is the central key decoder for `\xff/conf/` keys. It updates fields for proxy counts, logs, replication, engines, workers, regions, exclusions, wiggle, migration, and legacy `proxies`. `overwriteProxiesCount()` splits legacy total `proxies` into commit and GRV proxy counts using explicit overrides or default ratios. `applyMutation()`, `involveMutation()`, `set()`, and `clear()` apply mutations to the configuration view. `makeConfigurationMutable()` and `makeConfigurationImmutable()` convert between sorted `VectorRef<KeyValueRef>` and `std::map` representations.

## Control Flow

Reading from storage calls `fromKeyValues()`, which resets internals, stores raw key-values, applies each key through `setInternal()`, then fills default replication policies. Mutation application switches to mutable map form, updates or clears keys, and reparses when needed. JSON serialization is conditional: default values are omitted unless overridden, known redundancy modes compress multiple fields into a mode string, and backwards-compatible `proxies` is synthesized from commit/GRV counts.

## State And Persistence

The class mirrors persistent system keys under `configKeysPrefix` but does not write transactions itself. It stores either immutable raw configuration or mutable string maps, plus parsed derived fields. Exclusion helpers read excluded/failed server and locality keys from the same configuration snapshot.

## Dependencies And Integration Points

Dependencies include `DatabaseConfiguration.h`, `SystemData.h`, `FDBTypes.h`, Flow tracing/platform/unit-test support, replication policy serialization, status JSON helpers, and `CLIENT_KNOBS` defaults. It integrates with recruitment/recovery, configure command handling, status output, server exclusion logic, storage migration, backup worker enablement, and process-count selection.

## Risks And Test Signals

Parsing uses `atoi`/`atoll`/`atof` with FIXME sanity-check comments, so malformed numeric values may silently become zero. Several compatibility paths are subtle: legacy `proxies` splitting, ignored JSON fields in `configureStringFromJSON()`, missing `log_engine` fallback, and custom policy serialization. The included unit test `/fdbclient/databaseConfiguration/overwriteCommitProxy` verifies legacy proxy splitting equivalence. Additional test signals should cover invalid regions, duplicate datacenter IDs, satellite redundancy modes, excluded server/locality reads, clear-range reparse behavior, known redundancy JSON round trips, and tLog engine/spill validation.
