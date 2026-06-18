# sources/test-tools/syzkaller/pkg/vcs/linux.go

## Purpose

`linux.go` extends `gitRepo` with Linux-kernel-specific bisection, compiler selection, maintainer extraction, release tag handling, and kernel config minimization.

## Important APIs, Types, And Functions

`linux` embeds `*gitRepo` and stores `vmType`. `PreviousReleaseTags` filters old tags by compiler support. `gitParseReleaseTags` and `gitReleaseTagToInt` sort release tags. `EnvForCommit` selects compiler, adjusts config based on tags, and cherry-picks backports. `linuxClangPath` and `linuxGCCPath` map reachable tags to compiler versions. `PrepareBisect`, `Bisect`, `addMaintainers`, `getMaintainers`, `ParseMaintainersLinux`, and `Minimize` implement Linux-specific integration. `minimizeLinuxCtx` manages config minimization and instrumentation dropping.

## Control Flow, State, Dependencies, And Integration

The file mutates the checked-out kernel repo during backport cherry-picks and reads `scripts/get_maintainer.pl`. It parses Kconfig, serializes minimized configs with a syzkaller tag, and runs caller-provided bisection predicates. It depends on `targets`, `kconfig`, `crash.Type`, and `debugtracer`.

## Risks And Test Signals

Risks include stale compiler cutoff rules, upstream tag availability, get_maintainer output variability, expensive/flaky config minimization, and destructive repo operations inherited from Git. `linux_test.go`, `vcs_test.go`, and `linux_configs_test.go` cover compiler selection, maintainer parsing, release parsing, and sanitizer config behavior.
