## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistoryList.java

Purpose: persisted wrapper for a list of `ContainerReplicaHistory` records.

Important APIs/types/functions: static `getCodec`; constructor copies input list; `asList` returns unmodifiable view; `getList` returns mutable backing list; `fromProto`; `toProto`.

Control flow: `DelegatedCodec` wraps `Proto2Codec` for `ContainerReplicaHistoryListProto`; proto conversion maps each item through `ContainerReplicaHistory`.

State and persistence: durable codec for Recon DB table definitions storing replica history. Integrates with HDDS DB codec framework and protobuf types.

Risks: `getList` exposes mutable list, while `asList` is read-only; callers must choose carefully. Constructor does not null-check input. Tests should cover codec round-trip, list copy semantics, mutability via `getList`, unmodifiable `asList`, empty list, and null input behavior.
