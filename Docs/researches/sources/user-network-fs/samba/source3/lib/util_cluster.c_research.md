<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.c -->
# sources/user-network-fs/samba/source3/lib/util_cluster.c

## Purpose
`util_cluster.c` checks whether CTDB clustering is reachable when Samba is configured for clustering.

## Important APIs, types, and functions
The only exported function is `cluster_probe_ok`.

## Control flow
If `lp_clustering()` is false, the function returns true. If clustering is enabled, it calls `ctdbd_probe` with configured CTDB socket and timeout. A nonzero return logs a level-0 error and returns false.

## State and persistence behavior
No state is stored. The function only probes external CTDB daemon reachability.

## Dependencies and integration points
It depends on CTDB connection helpers, loadparm clustering settings, debug logging, and cluster support configuration. Startup or health-check paths use it to refuse clustered operation when CTDB is unavailable.

## Risks and edge cases
Probe failures may reflect socket path, timeout, daemon startup order, or permissions rather than permanent misconfiguration. The function is intentionally binary and does not retry.

## Test signals
Tests can mock `lp_clustering` and `ctdbd_probe` to validate no-op noncluster mode, success, and logged failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.c -->
