# sources/object-store/garage/src/garage/cli/remote/cluster.rs

Purpose: implements remote CLI cluster health, status, and node connection commands.

Important APIs/types/functions: `Cli::cmd_health`, `cmd_status`, and `cmd_connect`.

Control flow: health prints summary unless quiet and returns an error when status is `unavailable`. Status fetches cluster status and layout, prints healthy nodes, failed/pending/draining nodes, data availability, version info, staged layout changes, and operator hints. Connect sends a `ConnectClusterNodesRequest` for a single peer and prints success or failure.

State and persistence: health/status are read-only. Connect mutates cluster peer state by asking the target node to connect.

Dependencies and integration points: uses admin API cluster types, layout helper functions, `format_table`, `timeago`, `bytesize`, and shared `Cli::api_request`.

Risks: health status string comparison is literal. Status output combines live advertisements with layout roles and staged changes, so display correctness depends on API response consistency. Connect expects exactly one response.

Test signals: no local tests; cluster integration tests and manual CLI usage validate output and error handling.
