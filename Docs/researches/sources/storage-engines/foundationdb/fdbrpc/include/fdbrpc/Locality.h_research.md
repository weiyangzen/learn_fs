## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Locality.h

Purpose: Defines process classes, locality metadata, process descriptors, and load-balance locality traits used throughout cluster role assignment, replication placement, and endpoint routing.

Important APIs/types/functions: `ProcessClass` stores `ClassType` and `ClassSource`, maps classes to role fitness, serializes class/source enum values, and has static assertions preserving persisted enum numbers. `LocalityData` stores optional string attributes keyed by stable `StringRef`s such as process, zone, machine, data hall, and datacenter IDs. `ProcessData` bundles locality, class, network address, and optional gRPC address. `LBLocalityData` is a trait that detects interfaces with `LocationAwareLoadBalance`, and `loadBalanceDistance()` classifies endpoints as same-machine, same-DC, or distant.

Control flow: `LocalityData` is a map wrapper with getters, setters, descriptions, JSON conversion, and protocol-aware serialization. `ProcessClass` constructors parse strings elsewhere, while this header exposes getters and comparison operators. Load balancers use `LBLocalityData` specialization to extract locality/address from interfaces only when the interface opts in.

State and persistence behavior: `ProcessClass` and `LocalityData` are serialized into cluster metadata and restart info; comments and static assertions make enum stability a hard compatibility contract. `ProcessData` serialization is protocol-version gated for `grpcAddress`.

Dependencies and integration points: Depends on Flow serialization, `NetworkAddress`, and `Standalone<StringRef>`. Integrated by `MultiInterface`, replication locality maps, worker lists, simulator process metadata, status JSON, and role fitness logic.

Risks: Reordering `ClassType` or `ClassSource` breaks persisted data and upgrade tests. Locality serialization requires `ProtocolVersion::hasLocality()`. `LocalityData::isPresent(key, value)` appears inverted in the header (`pos != end ? false : ...`), so callers should be checked carefully if they rely on value-sensitive presence. Missing locality fields degrade placement/load-balance decisions to distant/default behavior.

Test signals: Upgrade serialization tests, role fitness matrix tests, JSON/status output checks, locality-distance tests, and worker-list compatibility tests are the most relevant.
