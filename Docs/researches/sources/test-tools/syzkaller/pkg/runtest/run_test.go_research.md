# sources/test-tools/syzkaller/pkg/runtest/run_test.go

## Purpose

This file provides end-to-end tests for `pkg/runtest`, local RPC execution, coverage/signal/comparison extraction, and parsing of sys test programs.

## Important APIs, Types, And Control Flow

Flags `-filter`, `-debug`, and `-gdb` select test subsets and executor diagnostics. `TestUnit` builds a test-OS executor and runs `Context.Run` over sys test files. `TestCover` defines `CoverTest` cases for 32/64-bit coverage, deduplication, signal hashing, invalid PCs, comparisons, max-signal filtering, cover filters, and extra coverage. Helpers `makeCover64`, `makeCover32`, and `makeComps` construct executor-injected binary payloads. `startRPCServer` creates a temp local `rpcserver.LocalConfig`, launches `RunLocal`, and returns a context used by queue requests. `TestParsing` parses all sys test files by OS/arch and checks C-source generation where possible.

## State, Dependencies, Risks, And Test Signals

The tests build executors, create local temp dirs, run RPC server goroutines, submit queue requests, and clean up executor work dirs with retries. Dependencies include `rpcserver`, `vminfo`, `csource`, `queue`, `flatrpc`, `prog`, `targets`, and `testutil`. Risks include compiler/toolchain availability, long runtime, race-mode narrowing, coverage order assumptions, and cleanup of executor subprocesses. Passing tests are a strong integration signal for executor protocol, coverage canonicalization, feature detection, and test-program parsing.
