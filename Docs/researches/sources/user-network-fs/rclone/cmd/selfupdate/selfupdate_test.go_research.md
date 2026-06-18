# sources/user-network-fs/rclone/cmd/selfupdate/selfupdate_test.go

Purpose: integration-tests self-update version resolution and executable replacement on Linux/Windows.

Important tests: `TestGetVersion` checks beta prefixing, stable semantic validation, and minor-to-latest-micro lookup. `TestInstallOnLinux` downloads beta to a temp output path, verifies no-op same-version, non-writable errors, permission preservation, temp cleanup, and executable version. `TestRenameOnWindows` checks `.old.exe` handling while executables are running and randomized old names.

State/persistence: downloads real release artifacts, writes temp executables, changes permissions, starts subprocesses, and relies on network/download site. Dependencies include `testy.SkipUnreliable`, `os/exec`, runtime platform checks, and fs.Version.

Risks/test signal: high-value end-to-end coverage but intentionally unreliable and platform-specific. It may be skipped often; failures can indicate network, permission, package availability, or Windows file-locking behavior rather than pure code regressions.
