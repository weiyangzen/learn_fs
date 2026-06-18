# sources/object-store/minio-mc/cmd/admin-replicate-status.go

## Purpose
Implements `mc admin replicate status`, the main site-replication health view for buckets, policies, users, groups, ILM expiry rules, and object replication metrics.

## Important APIs, types, and functions
Key symbols include `adminReplicateStatusFlags`, `srStatus`, `srStatus.String`, `siteHeader`, `getTheme`, per-entity summary helpers, `srStatusOpts`, `mainAdminReplicationStatus`, and `syncStatus`. It calls `SRStatusInfo`.

## Control flow
The command validates exactly one alias and mutually exclusive group versus individual entity flags. `srStatusOpts` defaults to all categories and metrics unless a specific selector is provided. The handler fetches `madmin.SRStatusInfo` and prints `srStatus`, whose renderer sorts site names, builds deployment-name maps, emits category summaries, optional per-entity detail tables, and object replication metrics including queue, worker, transfer, latency, link, and error data.

## State and persistence behavior
The command is read-only. It observes server-side replication configuration, metadata sync status, and realtime/summary replication metrics. Local state is only the selected options and formatting maps.

## Dependencies and integration points
It integrates MinIO site replication status APIs, replication metric types, pretty-table helpers, console color themes, humanized sizes/durations, global JSON mode, and global UTC time helpers.

## Risks and edge cases
Flag validation is complex and easy to regress. Some maps are indexed without explicit existence checks, so missing site/entity entries rely on zero-value stats. `strings.ToTitle` is deprecated in Go style. Queue warning logic compares current to average counts only.

## Test signals
Tests should cover default all view, category-only flags, individual entity flags, mutually exclusive validation, multiple individual selector rejection, disabled replication, bucket/user/group/policy/ILM mismatch rendering, metrics for single and multiple targets, offline link duration, and JSON output.
