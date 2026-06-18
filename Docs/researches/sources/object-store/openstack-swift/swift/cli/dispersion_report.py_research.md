# sources/object-store/openstack-swift/swift/cli/dispersion_report.py

Purpose: checks the dispersion resources created by `dispersion_populate` and reports what percentage of expected container/object replica copies are reachable on their primary nodes.

Important APIs: `get_error_log()`, `container_dispersion_report()`, `object_dispersion_report()`, `missing_string()`, `generate_report()`, and `main()`.

Control flow: `main()` reads config and option overrides, then `generate_report()` authenticates, builds a client pool, loads container and policy object rings, and calls selected report functions. Container report lists dispersion containers from the account, deduplicates by partition, and HEADs each primary container replica with `direct_client.retry()`. Object report lists objects in the policy-specific dispersion object container, deduplicates by object partition, and HEADs object replicas with optional backend policy headers. Both functions aggregate found/expected copies, missing-copy distribution, overlap count, retries, and optional JSON output.

State and persistence: read-only cluster probing. Module-level globals hold output/debug flags and de-duplicate unmounted/notfound error messages.

Dependencies and integration: uses direct client calls, storage policies, rings, SimpleClient auth, eventlet, and recon-style operator output. It consumes resources created by `dispersion_populate`.

Risks: reports only sampled partitions and primary nodes, so it is a health signal rather than a full audit. Missing 404 and 507 handling is intentionally special-cased. A policy object header is only used in object checks. Large samples can create many direct requests.

Test signals: cover empty-population warnings, JSON vs text outputs, missing partition printing, retry accounting, 404/507 suppression, overlapping partition math, policy selection, and config option overrides.
