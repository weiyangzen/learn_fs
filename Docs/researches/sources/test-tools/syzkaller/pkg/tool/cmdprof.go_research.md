# sources/test-tools/syzkaller/pkg/tool/cmdprof.go

## Purpose

`cmdprof.go` implements optional CPU and heap profiling setup for syzkaller command-line tools.

## Important APIs, Types, And Functions

`installProfiling(cpuprof, memprof string) func()` creates and starts a CPU profile when requested, returns a cleanup function, and layers heap profile writing after previous cleanup when `memprof` is requested. It uses `runtime.GC` before `pprof.WriteHeapProfile`.

## Control Flow, State, Dependencies, And Integration

State is process-global through `runtime/pprof`. Errors call `tool.Failf`, which writes to stderr and exits. The function is used by `tool.Init`, so command-line binaries can `defer tool.Init()()`.

## Risks And Test Signals

Profiling file creation or writing exits the process, which is appropriate for tools but hard to unit-test. CPU profile file close is omitted if `StartCPUProfile` fails after create, but the process exits. No direct tests cover profiling; integration is through command execution paths.
