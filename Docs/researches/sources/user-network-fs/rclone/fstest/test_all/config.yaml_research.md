
# sources/user-network-fs/rclone/fstest/test_all/config.yaml

Purpose: YAML matrix defining which rclone package tests run against which configured test remotes.

Important APIs/types/functions: top-level `tests` entries define package paths and flags such as `addbackend`, `nobinary`, `short`, `fastlist`, and `localonly`. `backends` entries map backend names to remotes and tune `fastlist`, `listretries`, `maxfile`, `extratime`, `oneonly`, `cleanup`, `env`, `tests`, `ignore`, and `ignoretests`.

Control flow: consumed by `runs.NewConfig` and expanded by `Config.MakeRuns`. `addbackend` makes the generic `backend` test path backend-specific. Backend `ignore` entries suppress known failing test names during retry/failure parsing; `ignoretests` prevents entire packages from running for a backend.

State/persistence: declarative only. It references external remotes, local Docker-backed remotes, and environment paths such as Kerberos config/ccache files.

Dependencies/integration: integrates with the rclone config file and the `fstest/testserver/init.d` scripts for names like `TestS3Minio`, `TestSFTPOpenssh`, `TestSMBKerberos`, `TestHdfs`, and WebDAV/Seafile servers.

Risks: stale ignore entries can hide regressions, while missing ignores can cause persistent known failures. Remote credentials/config must exist outside this file. Some commented entries document unavailable accounts or high rate-limit risk.

Test signals: this file is the authoritative signal for the intended integration-test coverage breadth and backend-specific exception policy.
