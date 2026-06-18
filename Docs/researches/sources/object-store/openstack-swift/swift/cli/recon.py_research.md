# sources/object-store/openstack-swift/swift/cli/recon.py

Purpose: cluster reconnaissance CLI that queries recon middleware endpoints on storage nodes discovered from rings and summarizes health, consistency, and operational metrics.

Important APIs: helpers `seconds2timeunit()` and `size_suffix()`, `Scout` for one-host HTTP requests, and `SwiftRecon` with checks for ring md5, swift.conf md5, async pendings, drive audit, unmounted devices, server type, expirer, reconstruction, replication, updater, auditor, object auditor, sharding, load, quarantine, socket usage, disk usage, time sync, and Swift versions. `main()` instantiates and runs `SwiftRecon`.

Control flow: CLI parses server types and check flags. For each server type, `_get_ring_names()` chooses relevant rings, `get_hosts()` extracts unique `(ip, port)` pairs with optional region/zone filters, and selected checks run through a `GreenPool`. `Scout.scout()` performs `GET /recon/<type>` and parses JSON; `scout_server_type()` sends `OPTIONS /`. Check methods aggregate returned values with `_gen_stats()`, print distributions, compare local file hashes, or identify mismatches.

State and persistence: read-only network probing plus local reads of ring files and `swift.conf`. It maintains only in-memory output and stats.

Dependencies and integration: recon middleware endpoints, Swift rings and storage policies, eventlet/urllib, local config hashes, and operator terminal output.

Risks: many assumptions about recon JSON keys can raise KeyError with older/newer middleware. `--all` can create broad concurrent polling across all storage nodes. Disk usage deduplicates by host and arbitrary port. Time checks depend on request latency bounds and configured jitter.

Test signals: mock `Scout` responses for each endpoint, no-host and partial-error cases, policy selection, region/zone filtering, hash mismatch, disk top/lowest output, auditor nested stats, and CLI flag gating per server type.
