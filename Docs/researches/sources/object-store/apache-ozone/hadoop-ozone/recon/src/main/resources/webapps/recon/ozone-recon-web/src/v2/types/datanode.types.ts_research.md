# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanode.types.ts

Purpose: Defines v2 datanode API rows, UI rows, operational state constants, decommission summary shapes, and table props.

Important APIs/types/functions: Exports `DatanodeStateList`/`DatanodeState`, `DatanodeOpStateList`/`DatanodeOpState`, `DatanodeResponse`, `DatanodesResponse`, `Datanode`, `DatanodeDetails`, `DatanodeDecomissionInfo`, `DatanodesState`, `SummaryData`, and `DatanodeTableProps`.

Control flow: Type-only module. It separates raw `DatanodeResponse.storageReport` from flattened `Datanode` storage fields used by tables. Summary types model `/api/v1/datanodes/decommission/info` style nested responses.

State and persistence: No runtime state. `DatanodesState` represents page-local table data and column options.

Dependencies and integration points: Imports `Pipeline`, `DatanodeStorageReport`, and multi-select `Option`. Constants correspond to HDDS node state and operational state enums.

Risks: The decommission spelling is inconsistent (`DatanodeDecomissionInfo`) and can propagate typos. `SummaryPort` is a single object, but backend details may expose multiple ports. Some summary fields are typed as broad `unknown | null` or nested ByteString-like internals, so components remain coupled to backend serialization details.

Test signals: Type/API fixture tests should cover each node state/op state, flattened storage transformations, decommission summary with and without metrics/containers, and table selection/search props.
