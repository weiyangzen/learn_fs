# sources/user-network-fs/rclone/fs/mount_helper_test.go

## Purpose
`mount_helper_test.go` verifies representative mount-helper argument conversion and environment handling.

## Important APIs, types, and functions
The test targets unexported `convertMountHelperArgs` and indirectly `parseHelperOptionString`. It checks output args and environment side effects.

## Control flow
`TestMountHelperArgs` defines normal cases, prepends a fake executable name, calls conversion, compares the command/flags after argv0, and checks any expected environment variable assignment.

## State and persistence behavior
The test may set environment variables such as `HTTPS_PROXY` in the process environment. It does not restore them in the shown code, so test isolation relies on chosen names and process lifetime.

## Dependencies and integration points
It uses `os.Getenv`, string splitting, and testify. The covered behavior protects rclone invocation through `/bin/mount` and systemd mount option strings.

## Risks and edge cases
Coverage is narrow relative to the parser: many error paths, quote failures, command override, explicit daemon handling, and unsupported flags are not exercised. The first normal case with no args confirms default `mount --daemon` behavior.

## Test signals
The positive case is high value because it combines `x-systemd` ignore, verbosity option, quoted env value with embedded separators, read-only alias, ignored mount options, and args-to-env mode.

Source-read signal: reviewed complete local file (53 lines). Types observed: `testCase`. Functions/methods observed: `TestMountHelperArgs`.
