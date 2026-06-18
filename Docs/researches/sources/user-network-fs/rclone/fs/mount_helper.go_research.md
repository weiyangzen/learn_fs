# sources/user-network-fs/rclone/fs/mount_helper.go

## Purpose
`mount_helper.go` converts Linux/Unix mount-helper invocation syntax into normal rclone command-line arguments. It lets rclone run as `mount.rclone` or `rclonefs` and parse `-o` option strings from `/bin/mount`, fusermount, or systemd mount units.

## Important APIs, types, and functions
Exports are `PassDaemonArgsAsEnviron` and `IsMountHelper`. Internal core functions are `convertMountHelperArgs` and `parseHelperOptionString`. Constants define ignored standard mount options and valid option-name characters; sentinel errors describe parser failures.

## Control flow
Package init detects mount-helper executable names early and rewrites `os.Args` unless already daemonized. `convertMountHelperArgs` scans original args, accepts `-o`/`--opt`, verbosity flags, and help, rejects other flags, parses option strings, ignores standard mount/systemd options, sets `env.NAME=value` environment variables, handles `command`, `args2env`, verbosity, `daemon`, `verbose`, and `ro`, converts remaining options to `--kebab-case` flags, defaults mount commands to `--daemon`, and returns `[argv0, command, ...]`.

## State and persistence behavior
It may mutate `os.Args`, environment variables, and `PassDaemonArgsAsEnviron`. It persists nothing to disk. `IsDaemon` integration avoids repeated conversion in daemon children.

## Dependencies and integration points
It integrates with rclone mount command startup, daemonization, config password prompt behavior, and OS mount helpers. The option parser borrows state-machine ideas from `fspath.Parse` but accepts mount-specific `env.` and `x-systemd.` prefixes.

## Risks and edge cases
This runs very early before normal configuration. Quoted option parsing, doubled quotes, dangling `-o`, unsupported flags, empty command names, and environment syntax are sensitive. `args2env` is a security feature to hide daemon args from process listings. Standard mount options must be ignored without swallowing meaningful rclone flags.

## Test signals
`mount_helper_test.go` covers empty conversion, quoted env values containing spaces/semicolons/commas, `ro`, ignored options, verbosity count, `args2env`, and default daemon insertion.

Source-read signal: reviewed complete local file (283 lines). Functions/methods observed: `init`, `IsMountHelper`, `convertMountHelperArgs`, `parseHelperOptionString`.
