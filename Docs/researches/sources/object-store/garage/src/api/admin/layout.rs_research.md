# sources/object-store/garage/src/api/admin/layout.rs

Purpose: implements cluster layout read/update/apply/revert/history operations and skip-dead-node tracker manipulation.

Important handlers/functions: `GetClusterLayoutRequest`, `format_cluster_layout`, `GetClusterLayoutHistoryRequest`, `UpdateClusterLayoutRequest`, `PreviewClusterLayoutChangesRequest`, `ApplyClusterLayoutRequest`, `RevertClusterLayoutRequest`, `ClusterLayoutSkipDeadNodesRequest`, and conversions between API and internal `layout::ZoneRedundancy/LayoutParameters`.

Control flow and state: layout state lives in Garage system `LayoutHistory`, including current versions, old versions, staging CRDTs, role maps, parameters, and update trackers. Update merges current roles with staging, validates node IDs and capacities, writes staged role/parameter changes through the layout manager, and returns formatted layout. Preview computes but does not persist staged changes. Apply computes a requested new version and persists it. Revert clears staging. Skip-dead-nodes advances ACK and optionally SYNC trackers for dead or all nodes to unblock old-layout retirement.

Dependencies/integration: depends on Garage RPC layout types, CRDT merge/update mutators, Garage system layout manager, node status, and admin schema role/parameter types.

Risks: layout changes affect placement and data movement. Capacity below 1024 is rejected, and zone redundancy must be between 1 and replication factor. Apply requires the caller-specified version as a safety check but still depends on current staging. `allow_missing_data` in skip-dead-nodes can mark sync progress despite missing data quorum, so it is operationally dangerous. Preview returns structured error for layout computation messages but propagates other errors.

Test signals: cover format output for current/staged roles and parameters, invalid node IDs/capacity/redundancy, update then preview/apply/revert, version mismatch on apply, history statuses current/draining/historical, tracker maps when multiple versions exist, and skip-dead-nodes with and without `allow_missing_data`.
