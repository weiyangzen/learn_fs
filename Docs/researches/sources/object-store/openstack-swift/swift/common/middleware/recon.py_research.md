# sources/object-store/openstack-swift/swift/common/middleware/recon.py

Purpose: Provides unauthenticated `/recon/...` monitoring endpoints for Swift account, container, and object servers, aggregating local system metrics, recon-cache JSON files, ring hashes, device state, and service version information.

Important APIs and control flow: `ReconMiddleware.__init__` derives devices, swift_dir, recon cache paths, and all ring paths including policy-specific object rings. `_from_recon_cache` reads selected keys from JSON cache files and returns `None` values on failures. Getter methods expose `/proc` load, memory, mounts, sockstat, current time, device listings, unmounted/disk usage via `check_mount`, quarantine counts via directory link counts, ring and swift.conf md5 sums, and recon cache groups for async, replication, reconstruction, updater, expirer, auditor, sharding, driveaudit, and relinker. `GET` dispatches based on `/recon/<check>/<type>`, serializes JSON, returns 404 for unknown paths, and 500 when a known handler returns `None`.

State, dependencies, and integration: Persistent inputs are recon cache JSON files, ring files, swift.conf, device directories, and `/proc`. It integrates with daemon-written recon files and storage policy configuration.

Risks and test signals: Endpoints reveal operational topology and should stay on trusted networks. Tests should cover missing and malformed cache files, ENOENT ignore behavior, device mount errors, ring hash IOError handling, quarantine link-count math, dispatch status codes, and policy ring inclusion.
