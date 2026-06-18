# sources/test-tools/syzkaller/vm/dispatcher/pool_test.go

## Purpose

`pool_test.go` verifies scheduler behavior for the generic dispatcher pool, especially restart, reservation, cancellation, pause, and race-prone state transitions.

## Important APIs, Types, and Functions

Tests include `TestPoolDefault`, `TestPoolSplit`, `TestPoolStress`, `TestPoolNewDefault`, `TestPoolPause`, `TestPoolCancelRun`, and `TestPoolBootErrors`. Helpers and fixtures include `makePool`, `testInstance`, `nilInstance`, `reset`, `run`, `waitRun`, `stopRun`, `Index`, and `Close`.

## Control Flow

The tests construct pools with fake instance creators and runner callbacks, start `Loop` in a goroutine, manipulate reservations and contexts, and use channels/atomics to assert expected scheduling. The stress tests intentionally interleave `TogglePause`, `Run`, and `ReserveForRun` to help the race detector.

## State and Persistence Behavior

All state is in-memory test fixture state. Fake instances expose stop channels and atomics so tests can observe job lifecycle without external VMs.

## Dependencies and Integration Points

It uses `testing`, `context`, `sync`, `atomic`, `runtime.Gosched`, and `testify/assert`. It is the main automated signal for `dispatcher.Pool`.

## Risks and Test Signals

The tests use polling sleeps, so pathological scheduler delays could cause slowness but not fixed timeouts in most cases. They do not verify `Info` callback contents or boot-time averages. Strong signals include all default slots restarting after job stop, custom jobs using only reserved slots, cancellation unblocking queued jobs, pause preventing start, and boot-error channel saturation not blocking shutdown.
