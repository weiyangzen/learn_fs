
# sources/user-network-fs/rclone/fstest/testy/testy.go

Purpose: small test utility package for CI and Docker availability gating.

Important APIs/types/functions: `CI` checks `CI` env var. `SkipUnreliable` skips tests on CI. `HaveDocker` caches whether Docker can be used by checking OS and `docker version`. `SkipUnlessDocker` skips tests when Docker is unavailable.

Control flow: `HaveDocker` uses `sync.Once`; Windows immediately returns false because init.d scripts are bash, otherwise it runs `docker version`.

State/persistence: cached in-memory `dockerOnce.ok`; no persistence.

Dependencies/integration: used by tests that require the fstest/testserver Docker framework.

Risks: `docker version` can be slow or fail for permission reasons. Cached false means Docker becoming available later in the same process is not detected.

Test signals: skip messages distinguish unavailable Docker and unreliable-on-CI tests.
