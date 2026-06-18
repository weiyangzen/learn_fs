# sources/storage-engines/tikv/components/tipb_helper/Cargo.toml

Purpose: Cargo manifest for the private `tipb_helper` crate.

Important APIs/types/functions: declares package metadata and workspace dependencies on `codec`, `tidb_query_datatype`, and `tipb`.

Control flow: no runtime control flow; the manifest wires the helper crate into the workspace dependency graph.

State and persistence: build metadata only.

Dependencies/integration: supports expression protobuf construction used by query-related code and tests.

Risks: dependency versions are inherited from the workspace, so helper behavior tracks workspace-wide codec/datatype/tipb changes.

Test signals: no manifest-local tests.
