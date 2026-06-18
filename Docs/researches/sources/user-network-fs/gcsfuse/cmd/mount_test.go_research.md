# sources/user-network-fs/gcsfuse/cmd/mount_test.go

## Purpose
`mount_test.go` tests `getFuseMountConfig`, the pure portion of mount configuration construction that can be validated without creating a real FUSE mount.

## Important APIs And Test Structure
`TestGetFuseMountConfig_MountOptionsFormattedCorrectly` checks that repeated `-o` inputs with comma-separated legacy format and new config-list format both produce the same parsed option map. `TestGetFuseMountConfig_LoggerInitializationInFuse` verifies GCSFuse log severity to FUSE logger setup: OFF installs no logger, ERROR and DEBUG install only error logging, and TRACE installs both error and debug logging. `TestGetFuseMountConfig_EnableReaddirplus` verifies the experimental ReaddirPlus flag passes into `fuse.MountConfig`.

## Control Flow And State
Tests construct minimal `cfg.Config` objects and call `getFuseMountConfig` with a fixed fs name. They inspect the returned in-memory `fuse.MountConfig` fields. No files are written, no wire log is opened, and no mount is attempted.

## Dependencies And Integration
The tests depend on cfg log severity and filesystem config structures, internal mount option parsing through `getFuseMountConfig`, and jacobsa/fuse mount config fields. They document the contract that command config values become FUSE mount options consumed by the kernel/FUSE library.

## Risks And Test Signals
The suite is intentionally narrow and does not cover temp-dir checks, UID/GID selection, gcsx bucket config, server construction, storage handles, or actual FUSE mounting. It is high-signal for option parsing and logger thresholds, two areas where small regressions are easy to introduce when changing config names or severity ranking.
