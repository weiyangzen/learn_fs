<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bisect/bisect.go -->
# sources/test-tools/syzkaller/tools/syz-bisect/bisect.go

## Purpose

Standalone driver for syzkaller crash cause/fix bisection.

## Important APIs, Types, and Functions

JSON `Config`; flags config/crash/fix/kernel/syzkaller commits; `loadFile`, `saveResultCommits`; `bisect.Run` with tracer.

## Control Flow

Loads configs, creates temp workdir if needed, loads repro/config files, defaults commits to HEAD, runs bisection, writes `cause.commit` or `fix.commit`.

## State and Persistence Behavior

Writes trace artifacts and result commit file in crash dir; may create temp manager workdir.

## Dependencies and Integration Points

Depends on repos, toolchains, userspace, manager config, and repro files.

## Risks and Edge Cases

Expensive and side-effectful; overwrites result files; missing both repro formats is fatal.

## Test Signals

Mock/tiny-repo tests and integration fixture for cause/fix outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bisect/bisect.go -->
