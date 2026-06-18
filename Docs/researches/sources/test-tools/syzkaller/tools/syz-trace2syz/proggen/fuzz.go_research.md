# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/fuzz.go

## Purpose

`fuzz.go` adds a libFuzzer-style entry point for the `proggen` package. It feeds arbitrary strace-like bytes into `ParseData` using a preinitialized Linux/amd64 syzkaller target, so parser and program-generation crashes can be found without running the command-line tool.

## Important APIs, Types, and Functions

The file defines package-level `linuxTarget`, `Fuzz(data []byte) int`, and `init`. `linuxTarget` calls `prog.GetTarget(targets.Linux, targets.AMD64)`, imports the syscall descriptions through a blank `sys` import, and builds `target.ConstMap` from target constants. `Fuzz` calls `ParseData` and returns zero on parse errors or the number of generated programs on success. `runtime.KeepAlive(Fuzz)` marks the entry as live for dead-code tooling.

## Control Flow

Initialization happens once at package load. Each fuzz input is parsed into the trace tree by `ParseData`, converted into one or more `prog.Prog` values by the rest of `proggen`, and collapsed to a simple coverage signal. Errors are intentionally not treated as fuzzing failures.

## State and Persistence Behavior

The only persistent state is the shared `linuxTarget` pointer and its constant map. Inputs, parsed traces, and generated programs are transient. There is no filesystem or network state.

## Dependencies and Integration Points

It depends on `prog`, `sys/targets`, the imported syscall descriptions, and `proggen.ParseData`. It integrates with Go fuzzing or syzkaller's dead-code analysis as a package-level fuzz harness.

## Risks and Test Signals

The fixed Linux/amd64 target means target-specific parser bugs for other OS/arch pairs are not covered. Because parse errors return zero, only panics, fatal exits, and unexpected internal failures are strong fuzz signals. Useful signals are fuzz corpora containing malformed strace syntax, nested groups, weird constants, and syscalls with union or resource arguments.
