# sources/object-store/garage/src/garage/cli/remote/node.rs

Purpose: implements remote CLI metadata snapshot command for nodes.

Important APIs/types/functions: `Cli::cmd_meta`.

Control flow: currently handles `MetaOperation::Snapshot { all }`, sends `CreateMetadataSnapshotRequest` to either `*` or the selected node, prints success/error table, and returns an error if any node failed.

State and persistence: triggers metadata snapshot creation on target node(s), causing server-side snapshot files to be written. CLI itself only prints results.

Dependencies and integration points: uses admin API local/multi snapshot request types, `hex` node encoding, `format_table`, and shared `Cli::api_request`.

Risks: all-node snapshot can partially fail; the command reports all results and returns an error if any failed. Snapshot path/lifecycle are controlled server-side, not visible here.

Test signals: no direct tests; admin local API tests and manual CLI validation cover it.
