# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_server_operations_

## Purpose

This symlink-target Munin plugin graphs per-second storage server operation counters for multiple Tahoe nodes.

## Important APIs, Types, and Functions

It discovers env `url_NODE` endpoints and derives `operation` from basename prefix `tahoe_server_operations_`. It reads `data["counters"]["storage_server.<operation>"]` and emits DERIVE fields with min zero.

## Control Flow

Config mode prints graph metadata and one series per node. Normal mode fetches every node stats endpoint and prints current counter values.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration is Munin symlinks such as `tahoe_server_operations_allocate`. Risks include bad symlink assertions, no network timeouts, node-name field issues, and missing counter keys. Tests should cover config/value modes, multiple nodes, and bad `argv[0]`.
