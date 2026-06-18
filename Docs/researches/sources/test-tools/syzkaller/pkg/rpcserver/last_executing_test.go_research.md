# sources/test-tools/syzkaller/pkg/rpcserver/last_executing_test.go

## Purpose

This test file verifies `LastExecuting` ring-buffer semantics and hanged-program retention.

## Important APIs, Types, And Flow

`TestLastExecutingEmpty` confirms an untouched tracker collects no records. `TestLastExecuting` records programs across several procs with a per-proc capacity of three and expects sorted records with older overflow removed and `Time` rewritten as time-before-latest. `TestLastExecutingHanged` verifies hanged programs survive later ring overwrites and receive synthetic proc IDs starting at `prog.MaxPids`.

## State, Dependencies, Risks, And Test Signals

The tests use fixed integer `time.Duration` values and byte-slice program labels, so expectations are deterministic. They do not test `PrependExecuting` offset changes or invalid proc indexes. Passing tests strongly signal that crash context preserves the latest per-proc executions and always includes hanged programs.
