# sources/test-tools/syzkaller/pkg/rpcserver/local.go

## Purpose

`local.go` runs a syz-executor process locally against the same `rpcserver` machinery used for remote VMs. It is used by runtest and executor integration tests to avoid a full manager/VM stack.

## Important APIs, Types, And Control Flow

`LocalConfig` embeds `Config` and adds executor path, run directory, interrupt handling, gdb mode, output capture, initial max signal/filter, and a `MachineChecked` callback. `RunLocal` sets up a local server, runs server and executor lifetimes together, and cancels the counterpart when either ends. `setupLocal` fills defaults, enables cover edges/filtering, listens on `:0`, and optionally wraps context cancellation around interrupts. `local` implements the `Manager` interface. `RunInstance` registers an instance, starts `executor runner <id> localhost <port>` or `gdb --args`, waits for RPC connection errors or context cancellation, kills the process on connection end, and returns executor/process errors.

## State, Dependencies, Integration, Risks, And Test Signals

State consists of a local server, setup synchronization channel, subprocess, and temp working directory owned by callers. Dependencies include `flatrpc`, `queue`, `osutil.HandleInterrupts`, `signal`, `vminfo`, and `os/exec`. It integrates with `pkg/runtest` and machine-check tests. Risks include process cleanup timing, gdb stdin/stdout behavior, missing executor binary, cancellation races, and returning a synthetic "executor process exited" error for normal exits unless context cancellation explains it. Tests in `runtest` and `rpcserver_test.go` exercise local setup, restart, machine check, and coverage flows.
