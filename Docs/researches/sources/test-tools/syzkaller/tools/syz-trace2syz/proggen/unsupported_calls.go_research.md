# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/unsupported_calls.go

## Purpose

`unsupported_calls.go` centralizes syscall names that `syz-trace2syz` intentionally skips. These calls are unsupported, unsafe, too environment-dependent, or not useful for seed generation.

## Important APIs, Types, and Functions

The file exports package-level `unsupportedCalls`, a `map[string]bool` consumed by `shouldSkip` in `proggen.go`. Entries include `execve`, `arch_prctl`, wait/futex/clone calls, memory mapping calls, selected signal calls, `getcwd`, `getcpu`, `rt_sigaction`, `set_robust_list`, and `set_tid_address`.

## Control Flow

During `genProg`, each parsed syscall is checked with `shouldSkip`. If its name is in this map, conversion logs a skip and does not append a syzkaller call.

## State and Persistence Behavior

The map is immutable after package initialization by convention. It has no persistence or side effects.

## Dependencies and Integration Points

It is coupled to parser syscall naming and syzkaller syscall descriptions. The list documents policy for trace conversion rather than runtime execution.

## Risks and Test Signals

Skipping may remove context needed by later calls, especially resource creation, memory setup, or signal state. Not skipping unsafe calls can produce programs that hang, fork away coverage, corrupt summaries, or depend on unrecoverable function pointers. Test signals are traces containing skipped calls followed by useful calls and ensuring conversion still produces valid programs.
