# sources/test-tools/syzkaller/pkg/vminfo/syscalls.go

## Purpose

`syscalls.go` orchestrates syscall support checking for a target VM. It provides the shared runtime primitives OS-specific checkers use to read VM files and execute small test programs.

## Important APIs, Types, And Functions

`checkContext` stores context, checker implementation, config, target, executor, virtual filesystem, result channels, and feature channel. `do` starts one goroutine per syscall, starts feature checks, submits required glob requests, collects syscall results, and finishes feature evaluation. Helpers include `rootCanOpen`, `canOpen`, `canWrite`, `supportedSyscalls`, `supportedOpenat`, `allOpenModes`, `callSucceeds`, `execCall`, `anyCallSucceeds`, sandbox guards, `val`, `execRaw`, `readFile`, `alwaysSupported`, and `extractStringConst`.

## Control Flow, State, Dependencies, And Integration

`do` builds a virtual filesystem from `flatrpc.FileInfo`, updates target glob expansions from executor glob requests, and returns enabled/disabled syscall maps plus feature results. `execRaw` chunks generated calls, deserializes them with the target, submits queue requests, and substitutes empty call info on failures.

## Risks And Test Signals

Goroutine-per-syscall behavior depends on executor progress; a blocked executor can block checks. Several helpers panic on malformed target descriptions or missing constants. Failed executor runs are treated as call failures, which can disable syscalls conservatively. `vminfo_test.go` limits program count and checks deduplication indirectly.
