# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_latency_

## Purpose

This symlink-target Munin plugin graphs a selected storage-server latency metric and percentile for multiple Tahoe nodes.

## Important APIs, Types, and Functions

The script discovers node stats URLs from env vars named `url_NODE`. It derives `operation` and `percentile` from its executable basename after prefix `tahoe_server_latency_`. Percentiles map to stats keys like `storage_server.latencies.<operation>.<percentile>_percentile`; `mean` maps to `mean`.

## Control Flow

It builds config labels for each node. Config mode prints graph metadata based on the derived operation/percentile. Normal mode fetches each node's `statistics?t=json`, reads `data["stats"][key]`, and prints one Munin value per node.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Integration is via symlinks such as `tahoe_server_latency_allocate_99_9`. Risks include assertion failure on wrong symlink name, `split("_", 1)` ambiguity if operation names contain underscores, no timeout, unsanitized node names, and KeyError on missing stats. Tests should invoke through fake `argv[0]` names for mean and percentile cases and fixture JSON per node.
