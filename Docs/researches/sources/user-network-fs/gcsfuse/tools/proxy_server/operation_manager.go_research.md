# sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager.go

Purpose: tracks retry instructions by request type and dispenses them according to skip and retry counts.

Important APIs/types/functions: `OperationManager`, `NewOperationManager`, `retrieveOperation`, and `addRetryConfig`.

Control flow: configs are grouped by `RequestType`. On retrieval, a mutex protects the slice; the first config either consumes skip count and returns empty, consumes retry count and returns its instruction, or is removed when exhausted before checking the next config.

State/persistence behavior: in-memory mutable retry counters are process state. No persistent files are written.

Dependencies/integration: called by `AddRetryID` for every HTTP request.

Risks/test signals: slice elements are copied into local `configs`; the code updates map only when dropping exhausted configs, but count mutations on `configs[0]` modify the shared underlying array, so behavior works but is subtle. Mutex makes per-process access safe.
