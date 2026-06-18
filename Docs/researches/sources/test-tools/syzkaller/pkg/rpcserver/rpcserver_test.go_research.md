# sources/test-tools/syzkaller/pkg/rpcserver/rpcserver_test.go

## Purpose

This file tests key `rpcserver` construction, handshake validation, and local machine-check restart behavior.

## Important APIs, Types, And Control Flow

`getTestDefaultCfg` builds a minimal test manager config. `TestNew` checks sandbox errors and feature flag derivation for remote coverage and memory dump settings. `TestCheckRevisions` validates architecture, git revision, and syscall revision mismatch errors. `TestHandleConn` uses `net.Pipe` and `flatrpc.Conn` to perform the cookie handshake and assert an unknown VM connection is rejected. `TestMachineCheckCrash` builds a test executor, starts a local server, kills an instance during machine check, restarts it, and waits for successful completion.

## State, Dependencies, Risks, And Test Signals

Tests depend on generated `mocks.Manager`, `prog` test targets, `csource.BuildExecutor`, `LocalConfig`, and `errgroup`. `TestMachineCheckCrash` is integration-heavy and can skip on broken compilers. The tests do not fully emulate normal runner execution or signal distribution, but they guard several high-risk setup paths: invalid config, version skew, unexpected VM IDs, and executor death during machine check.
