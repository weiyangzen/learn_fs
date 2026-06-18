<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/pd.rs -->
# sources/storage-engines/tikv/components/error_code/src/pd.rs

Purpose: this module defines Placement Driver error codes under `KV:Pd:`.

Important APIs and constants: constants include `IO`, `CLUSTER_BOOTSTRAPPED`, `CLUSTER_NOT_BOOTSTRAPPED`, `INCOMPATIBLE`, `GRPC`, `STREAM_DISCONNECT`, `REGION_NOT_FOUND`, `STORE_TOMBSTONE`, `DATA_COMPACTED`, `STALE_SERVICE_GC_SAFE_POINT`, and `UNKNOWN`, plus the generated `ALL_ERROR_CODES`.

Control flow and state: it is a declarative macro invocation with no conversion implementation. Runtime state is the lazy vector.

Dependencies and integration points: PD client and scheduling code can use these constants for cluster bootstrap, region lookup, safe-point, and gRPC connectivity errors. The generator binary includes this namespace.

Risks: some code suffixes contain spelling mistakes (`ClusterBootstraped`, `ClusterNotBootstraped`, `Imcompatible`) that may already be part of the stable external contract. Fixing them would be breaking for dashboards or support docs. Descriptions and workarounds are empty.

Test signals: no module-local tests exist. Compile-time macro expansion is the only direct signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/pd.rs -->
