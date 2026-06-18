# sources/test-tools/syzkaller/pkg/subsystem/raw_extractor.go

## Purpose

`raw_extractor.go` provides low-level subsystem lookup by source path and by syzkaller program contents. Higher-level extraction uses it as evidence collection for crash routing.

## Important APIs, Types, And Functions

`rawExtractor` contains a `PathMatcher` and a `perCall` map from syscall name to subsystems. `makeRawExtractor` builds both indexes from a subsystem list. `FromPath` delegates to `PathMatcher.Match`. `FromProg` calls `prog.CallSet`, then maps encountered call names to unique subsystem pointers.

## Control Flow, State, Dependencies, And Integration

Construction is in-memory. `FromProg` ignores parse errors returned by `prog.CallSet`, intentionally extracting whatever call set is available. The result list is built from a map, so order is unspecified. It integrates with `Extractor` voting and with subsystem lists that annotate relevant `Syscalls`.

## Risks And Test Signals

Risks include silent loss of syscall evidence when reproducer parsing fails, nondeterministic ordering, and exact-name dependency between `Subsystem.Syscalls` and `prog.CallSet` output. `raw_extractor_test.go` covers path rules, exclusion, overlapping path matches, and syscall extraction from representative syz programs.
