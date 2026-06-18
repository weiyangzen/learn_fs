# sources/user-network-fs/rclone/lib/file/unc_test.go

Source read signal: reviewed complete local file (48 lines, sha256 d78736617d55d870).

Purpose: Windows-only tests for UNC long-path conversion.

Important APIs/types/functions: Defines `uncTestPaths`, `uncTestPathsResults`, and `TestUncPaths`.

Control flow: Each input is converted with `UNCPath`, compared to expected output, then passed through `UNCPath` again to assert idempotence.

State and persistence behavior: No filesystem mutation; all paths are strings.

Dependencies and integration points: Uses Windows build tag and `testing`. It validates paths used by Windows file APIs for long path support.

Risks and test signals: Covers drive paths, already-long paths, UNC server/share paths, long components, and malformed-looking UNC inputs. Only runs on Windows.
