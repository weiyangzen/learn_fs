## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/ContainerCreateInfo.java

Purpose: Immutable value object recording a container's creation state and EC replica index for the witnessed-container metadata DB.

Important APIs and functions: `valueOf()` creates instances. `getCodec()`/`getNewCodec()` return a delegated protobuf codec. `getProtobuf()` lazily memoizes the protobuf representation. `getFromProtobuf()`, `getState()`, and `getReplicaIndex()` expose conversion and fields. `INVALID_REPLICA_INDEX` encodes legacy/no-index state.

Control flow and state: Instances hold final state, final replica index, and a memoized supplier for `ContainerProtos.ContainerCreateInfo`. The class is annotated immutable and exposes no mutators.

Persistence and dependencies: Persisted via `DelegatedCodec` over `Proto3Codec` in `WitnessedContainerMetadataStore`. It depends on container protobuf state enums and Ratis `MemoizedSupplier`.

Risks: `getNewCodec()` currently aliases `getCodec()`, so future codec migration must be intentional. Legacy records with invalid replica index require callers to interpret `-1` as no prior EC index. The protobuf supplier memoizes based on construction fields.

Test signals: Codec round trip, protobuf conversion, invalid replica index handling, immutability assumptions, and compatibility with previous string-valued witnessed-container table migration.
