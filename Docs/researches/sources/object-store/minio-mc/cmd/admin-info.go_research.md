# sources/object-store/minio-mc/cmd/admin-info.go

## Purpose
Implements `mc admin info`, displaying cluster/server health, version, network, drive, pool, erasure, and usage summaries.

## Important APIs, types, and functions
Important symbols are `adminInfoCmd`, `poolSummary`, `clusterInfo`, `clusterSummaryInfo`, `endpointToPools`, `clusterStruct`, `checkAdminInfoSyntax`, and `mainAdminInfo`. The handler calls `ServerInfo`.

## Control flow
The command validates a single target, fetches `madmin.InfoMessage`, wraps errors into `clusterStruct`, and prints through `printMsg`. Human rendering sorts servers, formats offline nodes separately, prints uptime/version/network/drives/pools for online nodes, builds an erasure-pool summary table, and appends cluster usage and online/offline drive counts.

## State and persistence behavior
The command is read-only. It observes server-reported runtime state and stored usage counters. The `--offline` flag filters output locally by skipping online server details.

## Dependencies and integration points
It integrates `madmin.InfoMessage` backend helpers, MinIO set utilities, console tables and colors, humanize/english pluralization, global JSON rendering, and shared admin client creation.

## Risks and edge cases
The cluster summary assumes backend arrays line up with pool indexes. Offline-only mode can hide useful aggregate context for online nodes. Development versions are redacted as `<development>`. Missing server info triggers fatal behavior in `String`.

## Test signals
Tests should exercise JSON success and error output, offline-only filtering, erasure and non-erasure backends, offline server rendering, pool summary capacity math, version redaction, and total usage/pluralization formatting.
