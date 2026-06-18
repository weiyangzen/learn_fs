# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen.go

## Purpose

`proggen.go` is the core trace-to-syzkaller-program converter. It reads parsed strace traces, selects matching syzkaller syscall descriptions, translates parser IR values into `prog.Arg` trees, tracks returned resources, and emits validated `prog.Prog` programs.

## Important APIs, Types, and Functions

Public entry points are `ParseFile` and `ParseData`. Main internals are `parseTree`, `genProg`, `context`, `(*context).genCall`, `Select`, `genResult`, `genArg`, `genVma`, `genArray`, `genStruct`, `recurseStructs`, `genUnionArg`, `genBuffer`, `genPtr`, `genConst`, `genResource`, `parseProc`, `addr`, and `shouldSkip`. It depends on `prog.Builder`, `prog.Type` implementations, `parser.TraceTree`, `parser.Syscall`, and call selectors from the same package.

## Control Flow

`ParseFile` reads bytes from disk and delegates to `ParseData`. `ParseData` parses strace bytes into a trace tree, then `parseTree` recursively walks the process hierarchy from `RootPid`, generating one syzkaller program per traced process. `genProg` skips paused and unsupported calls, sets current trace context, generates calls, appends them to a `prog.Builder`, and finalizes the program. `genCall` selects a syscall variant, creates a `prog.Call`, generates each argument from syzkaller type metadata and parsed IR, and caches positive resource returns.

## State and Persistence Behavior

`context` owns the mutable program builder, target, call selectors, return cache, and current source/destination call. Builder allocations provide stable virtual addresses for pointer/VMA arguments. The return cache links later resource arguments to earlier returned `prog.ResultArg` values using resource kind and trace expression. No state persists beyond one generated program.

## Dependencies and Integration Points

It integrates with `parser.ParseData`, syzkaller syscall descriptions, `prog.MakeProgGen`, `prog.Make*Arg` constructors, resource typing, and selector logic in companion files. The command-line `trace2syz.go`, tests, and fuzz harness are the direct callers.

## Risks and Test Signals

Many unexpected IR/type combinations call `log.Fatalf`, so malformed traces can terminate conversion instead of producing partial output. Buffer endian conversion, omitted struct fields, out-direction defaults, recursive struct wrapping, and resource reuse are correctness-sensitive. `proggen_test.go` supplies strong regression signals for open/write, pipe, socket variants, ioctl, sockaddr unions, device opens, xattrs, IPv4/IPv6 byte ordering, and unsupported or skipped calls.
