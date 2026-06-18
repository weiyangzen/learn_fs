# sources/user-network-fs/blobfuse2/component/azstorage/azstorage_constants.go

Purpose: centralizes metric/event field names and safe Azure SDK logging allowlists for the azstorage component.

Important APIs/types/functions: string constants name stats counters/events such as bytes downloaded/uploaded, progress events, filesystem operation names, open handles, and event fields (`mode`, `count`, `src`, `dest`, `size`, `target`). `allowedHeaders` and `allowedQueryParams` list request/response header and query names that may be logged without redaction.

Control flow: no executable control flow beyond package initialization of slices. Other azstorage files use these constants when pushing stats events and configuring SDK log redaction.

State and persistence behavior: package-level slices are initialized in memory. They do not persist state, but they influence what request metadata can appear in logs.

Dependencies/integration: used by azstorage operations and SDK logging helpers elsewhere in the package. The allowlists are security-sensitive integration points between Azure SDK diagnostics and BlobFuse logging.

Risks: allowlists include some SAS fields such as `se`, `sp`, `spr`, `srt`, `ss`, `st`, and `sv`, but exclude high-risk signature-like fields. Any future addition must be reviewed for secret leakage. Because slices are mutable package variables, accidental runtime modification is possible.

Test signals: no direct tests in this subset. Indirect signal comes from log behavior and operation stats tests elsewhere.
