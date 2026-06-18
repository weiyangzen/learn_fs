<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter.go

This file wraps Kopia CLI commands for repository, snapshot, server, ACL, and upgrade-related operations. `KopiaSnapshotter` owns a `Runner` and adds higher-level methods for connect/create, S3/filesystem modes, server startup, client authorization, snapshot create/restore/delete/list, GC, and parsing outputs.

Control flow builds CLI args with cache flags, no-update/progress flags, retention/parallel settings, and server control password. `CreateSnapshot` parses the snapshot ID from stdout or stderr. `ListSnapshots` cross-checks `manifest list` against `snapshot list --all`. Server mode generates TLS certs, waits for cert files and server status using retry loops, computes SHA-256 fingerprint, enables ACLs, and grants wildcard snapshot access. Helpers parse manifest IDs, snapshot list IDs, cert PEM, and "ACL already enabled" errors.

State is external Kopia config/repository/server process. Dependencies are `Runner`, `retry`, `crypto/x509`, CLI output formats, and environment. Risks include fragile output parsing, long retry timeouts, temp cert cleanup while server uses files, broad ACLs for tests, and command hangs without context deadlines. Tests cover parsing and executable integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter.go -->
