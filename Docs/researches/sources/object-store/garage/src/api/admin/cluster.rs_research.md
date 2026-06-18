# sources/object-store/garage/src/api/admin/cluster.rs

Purpose: implements cluster-wide status, health, statistics, and peer connection endpoints.

Important handlers: `GetClusterStatusRequest` merges known-node liveness with current and older layout roles to report nodes, roles, disk free space, and draining state. `GetClusterHealthRequest` maps system health into stable strings and counters. `GetClusterStatisticsRequest` computes bucket/object totals and cluster-wide available data/metadata estimates, returning both free-form text and structured fields. `ConnectClusterNodesRequest` asks the system layer to connect to provided node addresses.

Control flow and state: reads current cluster layout history, known node statuses, bucket table, object counter table, and ring assignment data. Availability estimates count partitions per node and use the minimum per-partition available bytes multiplied by partition count, marking results incomplete when any storage node lacks disk information. It avoids gathering per-bucket counters when there are 1000 or more buckets.

Dependencies/integration: uses `garage_rpc::layout`, partition constants, Garage system health and connect APIs, table enumeration, object counters, `bytesize`, and `format_table` for compatibility free-form output.

Risks: statistics are estimates and can be lower in practice; missing node disk info makes them imprecise. Large bucket counts skip object totals. Layout reads can fail or be unavailable, in which case parts of status/statistics degrade. Free-form output is maintained for compatibility and should not be treated as parseable.

Test signals: cover connected and disconnected nodes, nodes only in older layouts as draining, gateway vs storage roles, health status mapping, statistics with complete and missing disk info, bucket count above and below 1000, empty layouts, and connect success/failure aggregation.
